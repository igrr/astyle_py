import os
import re
import sys
import typing
from collections import namedtuple

from wasmtime import (
    Engine,
    ValType,
    Store,
    Linker,
    Module,
    Func,
    FuncType,
    Config,
    WasiConfig,
    Instance
)

from . import __version__


class WasmContext:
    def __init__(self):
        wasm_cfg = Config()
        wasm_cfg.cache = True
        self.linker = Linker(Engine(wasm_cfg))
        self.linker.define_wasi()
        self.store = Store(self.linker.engine)
        self.store.set_wasi(WasiConfig())
        self.inst = None  # type: typing.Optional[Instance]

    def call_func(self, name: str, *args):
        return self.inst.exports(self.store)[name](self.store, *args)

    def get_data_ptr(self, name: str):
        return self.inst.exports(self.store)[name].data_ptr(self.store)


class WasmString:
    def __init__(self, context: WasmContext, addr: int, len: int, as_str: str):
        self._context = context
        self._addr = addr
        self._len = len
        self._str = as_str

    def __del__(self):
        self._context.call_func("free", self._addr)

    @property
    def addr(self):
        return self._addr

    def __str__(self):
        return self._str

    @staticmethod
    def from_str(context: WasmContext, string: str) -> 'WasmString':
        strb = string.encode("utf-8") + b'\x00'
        n_bytes = len(strb)
        addr = int(context.call_func("malloc", n_bytes + 1))
        data = context.get_data_ptr("memory")
        for i in range(n_bytes):
            data[addr + i] = strb[i]
        data[addr + n_bytes] = 0
        return WasmString(context, addr, n_bytes, string)

    @staticmethod
    def from_addr(context: WasmContext, addr: int) -> 'WasmString':
        n_bytes = 0
        strb = bytearray()
        data = context.get_data_ptr("memory")
        while True:
            c = data[addr + n_bytes]
            if c == 0:
                break
            strb.append(c)
            n_bytes += 1
        string = strb.decode("utf-8")  # type: ignore
        return WasmString(context, addr, n_bytes, string)


class Astyle:
    def __init__(self):
        self.context = WasmContext()
        err_handler_type = FuncType([ValType.i32(), ValType.i32()], [])
        err_handler_func = Func(self.context.store, err_handler_type, self._err_handler)
        self.context.linker.define("env", "AStyleErrorHandler", err_handler_func)

        wasm_file = os.path.join(os.path.dirname(__file__), "libastyle.wasm")
        module = Module.from_file(self.context.store.engine, wasm_file)
        self.context.inst = self.context.linker.instantiate(self.context.store, module)
        self.context.call_func("_initialize")

        self._opts_ptr = WasmString.from_str(self.context, "")

    def version(self) -> str:
        res_addr = self.context.call_func("AStyleGetVersion")
        return str(WasmString.from_addr(self.context, res_addr))

    def set_options(self, options: str) -> None:
        self._opts_ptr = WasmString.from_str(self.context, options)

    def format(self, source: str) -> str:
        src_ptr = WasmString.from_str(self.context, source)
        res_addr = self.context.call_func("AStyleWrapper", src_ptr.addr, self._opts_ptr.addr)
        return str(WasmString.from_addr(self.context, res_addr))

    def _err_handler(self, errno: int, errptr: int):
        errstr = WasmString.from_addr(self.context, errptr)
        print("error: {} ({})".format(errstr, errno), file=sys.stderr)
        raise SystemExit(1)


def get_lines_from_file(fname: str) -> typing.List[str]:
    with open(fname) as f:
        return [line.strip() for line in f if not line.startswith("#") and len(line.strip()) > 0]


def pattern_to_regex(pattern: str) -> str:
    """
    Convert the CODEOWNERS-style path pattern into a regular expression string
    """
    orig_pattern = pattern  # for printing errors later

    # Replicates the logic from normalize_pattern function in Gitlab ee/lib/gitlab/code_owners/file.rb:
    if not pattern.startswith('/'):
        pattern = '/**/' + pattern
    if pattern.endswith('/'):
        pattern = pattern + '**/*'

    # Convert the glob pattern into a regular expression:
    # first into intermediate tokens
    pattern = (pattern.replace('**/', ':REGLOB:')
                      .replace('**', ':INVALID:')
                      .replace('*', ':GLOB:')
                      .replace('.', ':DOT:')
                      .replace('?', ':ANY:'))

    if pattern.find(':INVALID:') >= 0:
        raise ValueError("Likely invalid pattern '{}': '**' should be followed by '/'".format(orig_pattern))

    # then into the final regex pattern:
    re_pattern = (pattern.replace(':REGLOB:', '(?:.*/)?')
                         .replace(':GLOB:', '[^/]*')
                         .replace(':DOT:', '[.]')
                         .replace(':ANY:', '.') + '$')
    if re_pattern.startswith('/'):
        re_pattern = '^' + re_pattern

    return re_pattern


def file_excluded(fname: str, exclude_regexes: typing.Iterable[typing.Pattern[str]]) -> bool:
    for regex in exclude_regexes:
        if re.search(regex, "/" + fname):
            return True
    return False


AstyleArgs = namedtuple("AstyleArgs", [
    "options",
    "files",
    "exclude_list",
    "fix_formatting",
    "quiet"
])


def parse_args(args) -> AstyleArgs:
    i = 0
    for i, arg in enumerate(args):
        if not arg.startswith("--"):
            break
    else:
        i = len(args)

    options = args[:i]
    files = args[i:]
    exclude_list = []
    fix_formatting = True
    quiet = False
    options_to_remove = []

    for o in options:
        o_trimmed = o[2:] if o.startswith("--") else o
        parts = o_trimmed.split("=")
        opt = parts[0]
        value = parts[1] if len(parts) > 1 else None

        def ensure_value():
            if not value:
                raise ValueError("Option {} requires a value".format(opt))

        if opt == "dry-run":
            options_to_remove.append(o)
            fix_formatting = False

        elif opt == "options":
            options_to_remove.append(o)
            ensure_value()
            options += get_lines_from_file(value)

        elif opt == "exclude":
            options_to_remove.append(o)
            ensure_value()
            exclude_list.append(value)

        elif opt == "exclude-list":
            options_to_remove.append(o)
            ensure_value()
            exclude_list += get_lines_from_file(value)

        elif opt == "quiet":
            options_to_remove.append(o)
            quiet = True

    for o in options_to_remove:
        options.remove(o)

    return AstyleArgs(options=options, files=files, exclude_list=exclude_list, fix_formatting=fix_formatting, quiet=quiet)


def main():
    if "--version" in sys.argv:
        print(
            "astyle_py v{} with astyle v{}".format(
                __version__, Astyle().version()
            )
        )
        raise SystemExit(0)

    try:
        args = parse_args(sys.argv[1:])
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)

    exclude_regexes = [re.compile(pattern_to_regex(p)) for p in args.exclude_list]

    astyle = Astyle()
    astyle.set_options(" ".join(args.options))

    def diag(*args_):
        if not args.quiet:
            print(*args_, file=sys.stderr)

    files_with_errors = 0
    files_formatted = 0
    for fname in args.files:
        if file_excluded(fname, exclude_regexes):
            diag("Skipping {}".format(fname))
            continue
        with open(fname) as f:
            original = f.read()
        formatted = astyle.format(original)
        if formatted != original:
            if args.fix_formatting:
                diag("Formatting {}".format(fname))
                with open(fname, "w") as f:
                    f.write(formatted)
                files_formatted += 1
            else:
                diag("Formatting error in {}".format(fname))
                files_with_errors += 1

    if args.fix_formatting:
        if files_formatted:
            diag("Formatted {} files".format(files_formatted))
    else:
        if files_with_errors:
            diag("Formatting errors found in {} files".format(files_with_errors))
            raise SystemExit(1)
