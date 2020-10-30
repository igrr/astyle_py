import os
import sys
from wasmtime import Engine, ValType, WasiInstance, Store, \
    Linker, Module, Func, FuncType, Config, WasiConfig, ExitTrap


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


def main():
    wasm_cfg = Config()
    wasm_cfg.cache = True
    store = Store(Engine(wasm_cfg))
    linker = Linker(store)

    wasi_cfg = WasiConfig()
    inst = WasiInstance(store, "wasi_snapshot_preview1", wasi_cfg)
    linker.define_wasi(inst)

    inst = None

    def error_handler(errno, errptr):
        errstr = WasmString.from_addr(inst, errptr)
        print("error: %s (%d)" % (errno, errstr), file=sys.stderr)
        sys.exit(1)

    error_handler_func = Func(store, FuncType([ValType.i32(), ValType.i32()], []), error_handler)
    linker.define("env", "AStyleErrorHandler", error_handler_func)

    wasm_file = os.path.join(os.path.dirname(__file__), 'libastyle.wasm')
    module = Module.from_file(store.engine, wasm_file)
    inst = linker.instantiate(module)

    src = WasmString.from_str(inst, "int foo(void)\n{ int x = 2; return 32; }")
    opts = WasmString.from_str(inst, "--style=otbs")

    try:
        res_addr = inst.exports["AStyleGetVersion"]()
        print("Astyle version %s" % WasmString.from_addr(inst, res_addr))

        inst.exports["_initialize"]()
        res_addr = inst.exports["AStyleWrapper"](src.addr, opts.addr)
        print(WasmString.from_addr(inst, res_addr))
    except ExitTrap as trap:
        sys.exit(trap.code)

