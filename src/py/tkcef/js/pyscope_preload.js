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
    call(py_fn, kwargs = {}) {
        let call_id = Math.random().toString();
        this.retVals[call_id] = new PyCall();
        py_fn(call_id, this._complete_callback.bind(this), kwargs);
        console.log(py_fn);
        // window._pyscopeman.init_new(call_id, this._complete_callback.bind(this), kwargs);
        return new Promise((resolve, reject) => {
            this._checkValue(call_id, resolve, reject);
        });
    }
    _checkValue(call_id, resolve, reject) {
        let check = setInterval(() => {
            let call = this.retVals[call_id];
            if (call.completed) {
                let outcome = call.outcome;
                delete this.retVals[call_id];
                clearInterval(check);
                if (outcome['error'] !== null) {
                    outcome['error'];
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
console.log("loading scope manager");
window._scopeman = new PyScopeManager();
class PyScope {
    constructor(p_id = null) {
        this.id = p_id;
        this.create();
    }
    create() {
        return __awaiter(this, void 0, void 0, function* () {
            this.id = (yield window._scopeman.call(window._pyscopeman.create, { id: this.id }));
        });
    }
    destroy() {
        return __awaiter(this, void 0, void 0, function* () {
            this.id = (yield window._scopeman.call(window._pyscopeman.destroy, { id: this.id }));
        });
    }
    exec(code, ret_name = null, params = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.call(window._pyscopeman.exec, {
                "id": this.id,
                "code": code,
                "ret_name": ret_name,
                "params": params
            });
        });
    }
    do_func(code, params = {}) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.call(window._pyscopeman.do_func, {
                "id": this.id,
                "code": code,
                "params": params
            });
        });
    }
    make_func(name, code, params = []) {
        return __awaiter(this, void 0, void 0, function* () {
            let fn = yield window._scopeman.call(window._pyscopeman.make_func, {
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
            return yield window._scopeman.call(window._pyscopeman.get_var, {
                "id": this.id,
                "name": name
            });
        });
    }
    has_var(name) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.call(window._pyscopeman.has_var, {
                "id": this.id,
                "name": name
            });
        });
    }
    del_var(name) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.call(window._pyscopeman.del_var, {
                "id": this.id,
                "name": name
            });
        });
    }
    set_var(name, value) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.call(window._pyscopeman.set_var, {
                "id": this.id,
                "name": name,
                "value": name
            });
        });
    }
    call(name, args, kwargs) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield window._scopeman.call(window._pyscopeman.call, {
                "id": this.id,
                "name": name,
                "args": args,
                "kwargs": kwargs
            });
        });
    }
}
//# sourceMappingURL=pyscope_preload.js.map