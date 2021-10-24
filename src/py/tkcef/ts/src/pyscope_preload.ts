interface ReturnValues {
    [key: string]: _PyCall;
}

interface NewPyScopeInfo {
    name: string;
    is_new: boolean;
}

class _PyCall {
    completed: boolean;
    outcome: any;

    constructor() {
        this.completed = false;
        this.outcome = null;
    }
}

class _PyScopeManager {
    retVals: ReturnValues

    constructor() {
        this.retVals = {};
    }

    scope_call(scope_fn: Function, kwargs = {}) {
        let call_id: string = Math.random().toString();

        this.retVals[call_id] = new _PyCall();
        scope_fn(call_id, this._complete_callback.bind(this), kwargs);
        
        return new Promise((resolve: any, reject: any) => {
            this._checkValue(call_id, resolve, reject); 
        });
    }

    _checkValue (call_id: string, resolve: any, reject: any) {
        let return_interval_id = setInterval(() => {
           let call = this.retVals[call_id];
           if (call.completed) {
               let outcome = call.outcome;
               delete this.retVals[call_id];
               clearInterval(return_interval_id);

                if (outcome['error'] !== null){
                    let error = new Error(outcome['error'].message);
                    error.name = outcome['error'].name;
                    error.stack = outcome['error'].stack;
                    reject(error);

                }
                resolve(outcome['result']);
            }
        }, 100);
    }

    _complete_callback(call_id: string, result: any) {
        this.retVals[call_id].outcome = result;
        this.retVals[call_id].completed = true;
    }
}

console.log("Loading scope manager...");
window._scopeman = new _PyScopeManager();

class PyScope {
    id: string|null;
    allow_new: boolean;
    is_new: boolean|null;

    constructor(p_id: string|null = null, p_allow_new: boolean = false, responsible_to_destroy_if_new: boolean = true, p_auto_create: boolean = true) {
        this.id = p_id;
        this.allow_new = p_allow_new;
        this.is_new = null;
        if (p_auto_create) {
            this.create(responsible_to_destroy_if_new);
        }
    }

    async create(responsible_to_destroy_if_new: boolean = true) {
        let info: NewPyScopeInfo = <NewPyScopeInfo>(await window._scopeman.scope_call(window._py_scopeman.create, {id: this.id, allow_new: this.allow_new}));
        this.is_new = info.is_new;

        if (info.is_new) {
            this.id = info.name;
            if (responsible_to_destroy_if_new) {
                this.set_destroy_on_unload();
            }
        }
    }

    set_destroy_on_unload() {
        window.addEventListener("beforeunload", this.on_page_unload.bind(this), false);
    }

    async on_page_unload(e: any) {
        // If this window created a new scope, we need to destroy it to prevent memory leaks.
        window.py_print(`CEF is destroying ${this.id}...`);
        await this.destroy();
    }

    async destroy() {
        this.id = <string>(await window._scopeman.scope_call(window._py_scopeman.destroy, {id: this.id}));

    }

    async make_w_args(args: any[]) {
        let arg_ids: any[] = [];
        for (let i = 0; i < args.length; i++) {
            arg_ids.push(await JsObject(args[i]));
        }

        return arg_ids;
    }
    async make_w_kwargs(kwargs: any){
        let kwarg_ids: any = {};
        for (const [key, value] of Object.entries(kwargs)) {
            // Looking up both keys AND values from stored objects:
            kwarg_ids[key] = await JsObject(value);
        }

        return kwarg_ids;
    }

    async exec(code: string, params: any = {}, ret_name: string|null = null): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.exec, {
            "id": this.id,
            "code": code,
            "ret_name": ret_name,
            "params": params
        });
    }

    async aw_exec(code: string, params: any = {}, ret_name: string|null = null): Promise<any> {
        return await this.w_exec(code, params, ret_name, true);
    }

    async w_exec(code: string, params: any = {}, ret_name: string|null = null, do_auto_convert: boolean = false): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.w_exec_runner, {
            "id": this.id,
            "code": code,
            "ret_name": ret_name,
            "params": await this.make_w_kwargs(params),
            "do_auto_convert": do_auto_convert
        });
    }

    async do_func(code: string, params: any = {}): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.do_func, {
            "id": this.id,
            "code": code,
            "params": params
        });
    }

    async aw_do_func(code: string, params: any = {}): Promise<any> {
        return await this.w_do_func(code, params, true);
    }

    async w_do_func(code: string, params: any = {}, do_auto_convert: boolean = false): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.w_do_func_runner, {
            "id": this.id,
            "code": code,
            "params": await this.make_w_kwargs(params),
            "do_auto_convert": do_auto_convert
        });
    }

    async make_func(name: string, code: string, params: any = []): Promise<any> {
        let fn = await window._scopeman.scope_call(window._py_scopeman.make_func, {
            "id": this.id,
            "name": name,
            "code": code,
            "params": params
        });

        return fn;
    }

    async get_var(name: string): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.get_var, {
            "id": this.id,
            "name": name
        });
    }

    async has_var(name: string): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.has_var, {
            "id": this.id,
            "name": name
        });
    }

    async del_var(name: string): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.del_var, {
            "id": this.id,
            "name": name
        });
    }

    async set_var(name: string, value: any): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.set_var, {
            "id": this.id,
            "name": name,
            "value": value
        });
    }

    async call(name: string, ...args: string[]) {
        return await this.call_kw(name, args);
    }

    async call_kw(name: string, args: any[] = [], kwargs: any = {}): Promise<any> {
        return await window._scopeman.scope_call(window._py_scopeman.raw_call_runner, {
            "id": this.id,
            "name": name,
            "args": args,
            "kwargs": kwargs
        });
    }

    async aw_call(name: string, ...args: string[]): Promise<any> {
        return await this.w_call_kw(name, args, {}, true);
    }

    async aw_call_kw(name: string, args: any[] = [], kwargs: any = {}): Promise<any> {
        return await this.w_call_kw(name, args, kwargs, true);
    }

    async w_call(name: string, ...args: string[]): Promise<any> {
        return await this.w_call_kw(name, args);
    }



    async w_call_kw(name: string, args: any[] = [], kwargs: any = {}, auto_convert: boolean = false): Promise<any> {
        // return await window._scopeman.scope_call(window._py_scopeman.w_call_runner, {
        return await window._scopeman.scope_call(window._py_scopeman.w_call_runner, {
            "id": this.id,
            "name": name,
            "args": await this.make_w_args(args),
            "kwargs": await this.make_w_kwargs(kwargs),
            "auto_convert": auto_convert
        });
    }

}

const py = new PyScope(window.app_scope_key);