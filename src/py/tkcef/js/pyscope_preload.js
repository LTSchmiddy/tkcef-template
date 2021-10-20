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
class PyCall {
    constructor() {
        this.completed = false;
        this.outcome = null;
    }
}
class PyScopeManager {
    constructor() {
        this.retVals = {};
    }
    scope_call(scope_fn, kwargs = {}) {
        let call_id = Math.random().toString();
        this.retVals[call_id] = new PyCall();
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
window._scopeman = new PyScopeManager();
class PyScope {
    constructor(p_id = null, p_allow_new = false, responsible_to_destroy_if_new = true, p_auto_create = true) {
        this.id = p_id;
        this.allow_new = p_allow_new;
        this.is_new = null;
        if (p_auto_create) {
            this.create(responsible_to_destroy_if_new);
        }
    }
    create(responsible_to_destroy_if_new) {
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
    exec(code, ret_name = null, params = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.exec, {
                "id": this.id,
                "code": code,
                "ret_name": ret_name,
                "params": params
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
    call(name, args = [], kwargs = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.scope_call(window._py_scopeman.call, {
                "id": this.id,
                "name": name,
                "args": args,
                "kwargs": kwargs
            });
        });
    }
}
let app_scope = new PyScope(window.app_scope_key);
//# sourceMappingURL=pyscope_preload.js.map