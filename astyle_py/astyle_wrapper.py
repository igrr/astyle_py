# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import os
import sys
import typing

from wasmtime import (
    Config,
    Engine,
    Func,
    FuncType,
    Instance,
    Linker,
    Module,
    Store,
    ValType,
    WasiConfig,
)


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
        return self.inst.exports(self.store)[name](self.store, *args)  # type: ignore

    def get_data_ptr(self, name: str):
        return self.inst.exports(self.store)[name].data_ptr(self.store)  # type: ignore


class WasmString:
    def __init__(self, context: WasmContext, addr: int, len: int, as_str: str):
        self._context = context
        self._addr = addr
        self._len = len
        self._str = as_str

    def __del__(self):
        self._context.call_func('free', self._addr)

    @property
    def addr(self):
        return self._addr

    def __str__(self):
        return self._str

    @staticmethod
    def from_str(context: WasmContext, string: str) -> 'WasmString':
        strb = string.encode('utf-8') + b'\x00'
        n_bytes = len(strb)
        addr = int(context.call_func('malloc', n_bytes + 1))
        data = context.get_data_ptr('memory')
        for i in range(n_bytes):
            data[addr + i] = strb[i]
        data[addr + n_bytes] = 0
        return WasmString(context, addr, n_bytes, string)

    @staticmethod
    def from_addr(context: WasmContext, addr: int) -> 'WasmString':
        n_bytes = 0
        strb = bytearray()
        data = context.get_data_ptr('memory')
        while True:
            c = data[addr + n_bytes]
            if c == 0:
                break
            strb.append(c)
            n_bytes += 1
        string = strb.decode('utf-8')  # type: ignore
        return WasmString(context, addr, n_bytes, string)


ASTYLE_COMPAT_VERSION = '3.1'
ASTYLE_SUPPORTED_VERSIONS = os.listdir(os.path.join(os.path.dirname(__file__), 'lib'))


class Astyle:
    def __init__(self, version: str = ASTYLE_COMPAT_VERSION):
        if version not in ASTYLE_SUPPORTED_VERSIONS:
            raise ValueError(
                'Unsupported astyle version: {}. Available versions: {}'.format(
                    version, ', '.join(ASTYLE_SUPPORTED_VERSIONS)
                )
            )

        self.context = WasmContext()
        err_handler_type = FuncType([ValType.i32(), ValType.i32()], [])
        err_handler_func = Func(self.context.store, err_handler_type, self._err_handler)
        self.context.linker.define('env', 'AStyleErrorHandler', err_handler_func)

        wasm_file = os.path.join(
            os.path.dirname(__file__), 'lib', version, 'libastyle.wasm'
        )
        module = Module.from_file(self.context.store.engine, wasm_file)
        self.context.inst = self.context.linker.instantiate(self.context.store, module)
        self.context.call_func('_initialize')

        self._opts_ptr = WasmString.from_str(self.context, '')

    def version(self) -> str:
        res_addr = self.context.call_func('AStyleGetVersion')
        return str(WasmString.from_addr(self.context, res_addr))

    def set_options(self, options: str) -> None:
        self._opts_ptr = WasmString.from_str(self.context, options)

    def format(self, source: str) -> str:
        src_ptr = WasmString.from_str(self.context, source)
        res_addr = self.context.call_func(
            'AStyleWrapper', src_ptr.addr, self._opts_ptr.addr
        )
        return str(WasmString.from_addr(self.context, res_addr))

    def _err_handler(self, errno: int, errptr: int):
        errstr = WasmString.from_addr(self.context, errptr)
        print('error: {} ({})'.format(errstr, errno), file=sys.stderr)
        raise SystemExit(1)
