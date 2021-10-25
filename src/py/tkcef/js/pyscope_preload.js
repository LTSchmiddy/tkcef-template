"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
class _PyCall {
    constructor() {
        this.completed = false;
        this.outcome = null;
    }
}
class _PyScopeManager {
    constructor() {
        this.retVals = {};
    }
    scope_call(scope_fn, kwargs = {}) {
        let call_id = Math.random().toString();
        this.retVals[call_id] = new _PyCall();
        scope_fn(call_id, this._complete_callback.bind(this), kwargs);
        return new Promise((resolve, reject) => {
            this._checkValue(call_id, resolve, reject);
        });
    }
    _checkValue(call_id, resolve, reject) {
        let return_interval_id = setInterval(() => {
            let call = this.retVals[call_id];
            if (call.completed) {
                let outcome = call.outcome;
                delete this.retVals[call_id];
                clearInterval(return_interval_id);
                if (outcome['error'] !== null) {
                    let error = new Error(outcome['error'].message);
                    error.name = outcome['error'].name;
                    error.stack = outcome['error'].stack;
                    reject(error);
                }
                resolve(outcome['result']);
            }
        }, 100);
    }
    _complete_callback(call_id, result) {
        this.retVals[call_id].outcome = result;
        this.retVals[call_id].completed = true;
    }
}
console.log("Loading scope manager...");
window._scopeman = new _PyScopeManager();
class PyScope {
    constructor(p_id = null, p_allow_new = false, responsible_to_destroy_if_new = true, p_auto_create = true) {
        this.id = p_id;
        this.allow_new = p_allow_new;
        this.is_new = null;
        if (p_auto_create) {
            this.create(responsible_to_destroy_if_new);
        }
    }
    create(responsible_to_destroy_if_new = true) {
        return __awaiter(this, void 0, void 0, function* () {
            let info = (yield window._scopeman.scope_call(window._py_scopeman.create, { id: this.id, allow_new: this.allow_new }));
            this.is_new = info.is_new;
            if (info.is_new) {
                this.id = info.name;
                if (responsible_to_destroy_if_new) {
                    this.set_destroy_on_unload();
                }
            }
        });
    }
    set_destroy_on_unload() {
        window.addEventListener("beforeunload", this.on_page_unload.bind(this), false);
    }
    on_page_unload(e) {
        return __awaiter(this, void 0, void 0, function* () {
            // If this window created a new scope, we need to destroy it to prevent memory leaks.
            window.py_print(`CEF is destroying ${this.id}...`);
            yield this.destroy();
        });
    }
    destroy() {
        return __awaiter(this, void 0, void 0, function* () {
            this.id = (yield window._scopeman.scope_call(window._py_scopeman.destroy, { id: this.id }));
        });
    }
    make_w_args(args) {
        return __awaiter(this, void 0, void 0, function* () {
            let arg_ids = [];
            for (let i = 0; i < args.length; i++) {
                arg_ids.push(yield JsObject(args[i]));
            }
            return arg_ids;
        });
    }
    make_w_kwargs(kwargs) {
        return __awaiter(this, void 0, void 0, function* () {
            let kwarg_ids = {};
            for (const [key, value] of Object.entries(kwargs)) {
                // Looking up both keys AND values from stored objects:
                kwarg_ids[key] = yield JsObject(value);
            }
            return kwarg_ids;
        });
    }
    exec(code, params = {}, ret_name = null) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.exec, {
                "id": this.id,
                "code": code,
                "ret_name": ret_name,
                "params": params
            });
        });
    }
    aw_exec(code, params = {}, ret_name = null) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this.w_exec(code, params, ret_name, true);
        });
    }
    w_exec(code, params = {}, ret_name = null, do_auto_convert = false) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.w_exec_runner, {
                "id": this.id,
                "code": code,
                "ret_name": ret_name,
                "params": yield this.make_w_kwargs(params),
                "do_auto_convert": do_auto_convert
            });
        });
    }
    do_func(code, params = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.do_func, {
                "id": this.id,
                "code": code,
                "params": params
            });
        });
    }
    aw_do_func(code, params = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this.w_do_func(code, params, true);
        });
    }
    w_do_func(code, params = {}, do_auto_convert = false) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.w_do_func_runner, {
                "id": this.id,
                "code": code,
                "params": yield this.make_w_kwargs(params),
                "do_auto_convert": do_auto_convert
            });
        });
    }
    make_func(name, code, params = []) {
        return __awaiter(this, void 0, void 0, function* () {
            let fn = yield window._scopeman.scope_call(window._py_scopeman.make_func, {
                "id": this.id,
                "name": name,
                "code": code,
                "params": params
            });
            return fn;
        });
    }
    get_var(name) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.get_var, {
                "id": this.id,
                "name": name
            });
        });
    }
    has_var(name) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.has_var, {
                "id": this.id,
                "name": name
            });
        });
    }
    del_var(name) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.del_var, {
                "id": this.id,
                "name": name
            });
        });
    }
    set_var(name, value) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.set_var, {
                "id": this.id,
                "name": name,
                "value": value
            });
        });
    }
    call(name, ...args) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this.call_kw(name, args);
        });
    }
    call_kw(name, args = [], kwargs = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.raw_call_runner, {
                "id": this.id,
                "name": name,
                "args": args,
                "kwargs": kwargs
            });
        });
    }
    aw_call(name, ...args) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this.w_call_kw(name, args, {}, true);
        });
    }
    aw_call_kw(name, args = [], kwargs = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this.w_call_kw(name, args, kwargs, true);
        });
    }
    w_call(name, ...args) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this.w_call_kw(name, args);
        });
    }
    w_call_kw(name, args = [], kwargs = {}, auto_convert = false) {
        return __awaiter(this, void 0, void 0, function* () {
            // return await window._scopeman.scope_call(window._py_scopeman.w_call_runner, {
            return yield window._scopeman.scope_call(window._py_scopeman.w_call_runner, {
                "id": this.id,
                "name": name,
                "args": yield this.make_w_args(args),
                "kwargs": yield this.make_w_kwargs(kwargs),
                "auto_convert": auto_convert
            });
        });
    }
}
const py = new PyScope(window.app_scope_key);
//# sourceMappingURL=pyscope_preload.js.map