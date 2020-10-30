import os
import re
import sys
from wasmtime import (
    Engine,
    ValType,
    WasiInstance,
    Store,
    Linker,
    Module,
    Func,
    FuncType,
    Config,
    WasiConfig,
)
from . import __version__


class WasmString:
    def __init__(self, inst, addr, len, as_str):
        self._inst = inst
        self._addr = addr
        self._len = len
        self._str = as_str

    def __del__(self):
        self._inst.exports["free"](self._addr)

    @property
    def addr(self):
        return self._addr

    def __str__(self):
        return self._str

    @staticmethod
    def from_str(inst, string):
        strb = string.encode("utf-8")
        n_bytes = len(strb)
        addr = inst.exports["malloc"](n_bytes + 1)
        data = inst.exports["memory"].data_ptr
        for i in range(n_bytes):
            data[addr + i] = strb[i]
        data[addr + n_bytes] = 0
        return WasmString(inst, addr, n_bytes, string)

    @staticmethod
    def from_addr(inst, addr):
        n_bytes = 0
        strb = []
        data = inst.exports["memory"].data_ptr
        while True:
            c = data[addr + n_bytes]
            if c == 0:
                break
            strb.append(c)
            n_bytes += 1
        string = bytes(strb).decode("utf-8")
        return WasmString(inst, addr, n_bytes, string)


class Astyle:
    def __init__(self):
        wasm_cfg = Config()
        wasm_cfg.cache = True
        store = Store(Engine(wasm_cfg))
        linker = Linker(store)

        wasi_cfg = WasiConfig()
        wasi_inst = WasiInstance(store, "wasi_snapshot_preview1", wasi_cfg)
        linker.define_wasi(wasi_inst)

        self.inst = None
        err_handler_type = FuncType([ValType.i32(), ValType.i32()], [])
        err_handler_func = Func(store, err_handler_type, self._err_handler)
        linker.define("env", "AStyleErrorHandler", err_handler_func)

        wasm_file = os.path.join(os.path.dirname(__file__), "libastyle.wasm")
        module = Module.from_file(store.engine, wasm_file)
        self.inst = linker.instantiate(module)
        self.inst.exports["_initialize"]()

        self._opts_ptr = WasmString.from_str(self.inst, "")

    def version(self):
        res_addr = self.inst.exports["AStyleGetVersion"]()
        return str(WasmString.from_addr(self.inst, res_addr))

    def set_options(self, options):
        self._opts_ptr = WasmString.from_str(self.inst, options)

    def format(self, source):
        src_ptr = WasmString.from_str(self.inst, source)
        fmt_func = self.inst.exports["AStyleWrapper"]
        res_addr = fmt_func(src_ptr.addr, self._opts_ptr.addr)
        return str(WasmString.from_addr(self.inst, res_addr))

    def _err_handler(self, errno, errptr):
        errstr = WasmString.from_addr(self.inst, errptr)
        print("error: {} ({})".format(errstr, errno), file=sys.stderr)
        raise SystemExit(1)


def get_lines_from_file(fname):
    with open(fname) as f:
        return [line.strip() for line in f if not line.startswith("#") and len(line.strip()) > 0]


def pattern_to_regex(pattern):
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


def file_excluded(fname, exclude_regexes):
    for regex in exclude_regexes:
        if re.search(regex, "/" + fname):
            return True
    return False


def main():
    if "--version" in sys.argv:
        print(
            "astyle_py v{} with astyle v{}".format(
                __version__, Astyle().version()
            )
        )
        raise SystemExit(0)

    for i, arg in enumerate(sys.argv[1:], 1):
        if not arg.startswith("--"):
            break

    options = sys.argv[1:i]
    files = sys.argv[i:]
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
                print("Option {} requires a value".format(opt), file=sys.stderr)
                raise SystemExit(1)

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

    exclude_regexes = [re.compile(pattern_to_regex(p)) for p in exclude_list]

    astyle = Astyle()
    astyle.set_options(" ".join(options))

    def diag(*args):
        if not quiet:
            print(*args, file=sys.stderr)

    files_with_errors = 0
    files_formatted = 0
    for fname in files:
        if file_excluded(fname, exclude_regexes):
            diag("Skipping {}".format(fname))
            continue
        with open(fname) as f:
            original = f.read()
        formatted = astyle.format(original)
        if formatted != original:
            if fix_formatting:
                diag("Formatting {}".format(fname))
                with open(fname, "w") as f:
                    f.write(formatted)
                files_formatted += 1
            else:
                diag("Formatting error in {}".format(fname))
                files_with_errors += 1

    if fix_formatting:
        if files_formatted:
            diag("Formatted {} files".format(files_formatted))
    else:
        if files_with_errors:
            diag("Formatting errors found in {} files".format(files_with_errors))
            raise SystemExit(1)
