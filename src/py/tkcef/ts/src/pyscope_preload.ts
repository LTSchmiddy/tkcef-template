interface ReturnValues {
    [key: string]: PyCall;
}

class PyCall {
    completed: boolean;
    outcome: any;

    constructor() {
        this.completed = false;
        this.outcome = null;
    }
}

class PyScopeManager {
    retVals: ReturnValues

    constructor() {
        this.retVals = {};
    }

    call(py_fn: Function, kwargs = {}) {
        let call_id: string = Math.random().toString();

        this.retVals[call_id] = new PyCall();
        py_fn(call_id, this._complete_callback.bind(this), kwargs);
        console.log(py_fn);
        // window._pyscopeman.init_new(call_id, this._complete_callback.bind(this), kwargs);
        
        return new Promise((resolve: any, reject: any) => {
            this._checkValue(call_id, resolve, reject); 
        });
    }

    _checkValue (call_id: string, resolve: any, reject: any) {
        let check = setInterval(() => {
           let call = this.retVals[call_id];
           if (call.completed) {
               let outcome = call.outcome;
               delete this.retVals[call_id];
               clearInterval(check);

                if (outcome['error'] !== null){
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

    _complete_callback(call_id: string, result: any) {
        this.retVals[call_id].outcome = result;
        this.retVals[call_id].completed = true;
    }
}

console.log("loading scope manager");
window._scopeman = new PyScopeManager();

class PyScope {
    id: string|null;

    constructor(p_id: string|null = null) {
        this.id = p_id;
        this.create();
    }

    async create() {
        this.id = <string>(await window._scopeman.call(window._pyscopeman.create, {id: this.id}));

    }

    async destroy() {
        this.id = <string>(await window._scopeman.call(window._pyscopeman.destroy, {id: this.id}));

    }

    async exec(code: string, ret_name: string|null = null, params: any = {}): Promise<any> {
        return await window._scopeman.call(window._pyscopeman.exec, {
            "id": this.id,
            "code": code,
            "ret_name": ret_name,
            "params": params
        });
    }

    async do_func(code: string, params: any = {}): Promise<any> {
        return await window._scopeman.call(window._pyscopeman.do_func, {
            "id": this.id,
            "code": code,
            "params": params
        });
    }

    async make_func(name: string, code: string, params: any = []): Promise<any> {
        let fn = await window._scopeman.call(window._pyscopeman.make_func, {
            "id": this.id,
            "name": name,
            "code": code,
            "params": params
        });

        return fn;
    }

    async get_var(name: string): Promise<any> {
        return await window._scopeman.call(window._pyscopeman.get_var, {
            "id": this.id,
            "name": name
        });
    }

    async has_var(name: string): Promise<any> {
        return await window._scopeman.call(window._pyscopeman.has_var, {
            "id": this.id,
            "name": name
        });
    }

    async del_var(name: string): Promise<any> {
        return await window._scopeman.call(window._pyscopeman.del_var, {
            "id": this.id,
            "name": name
        });
    }

    async set_var(name: string, value: any): Promise<any> {
        return await window._scopeman.call(window._pyscopeman.set_var, {
            "id": this.id,
            "name": name,
            "value": name
        });
    }

    async call(name: string, args: any, kwargs: any): Promise<any> {
        return await window._scopeman.call(window._pyscopeman.call, {
            "id": this.id,
            "name": name,
            "args": args,
            "kwargs": kwargs
        });
    }

}


