interface ObjectStorage {
    [key: string]: any;
}

class JsObjectManager {
    storage: ObjectStorage;
    
    callback_errors: boolean;

    constructor() {
        this.storage = {};
        this.callback_errors = true;
        window._py_jsobjectman.append_callback("fadd_fn", this._fadd_fn.bind(this));
        window._py_jsobjectman.append_callback("add_fn", this._add_fn.bind(this));
        window._py_jsobjectman.append_callback("remove_fn", this._remove_fn.bind(this));
        window._py_jsobjectman.append_callback("access_fn", this._access_fn.bind(this));
        window._py_jsobjectman.append_callback("py_fn", this._py_fn.bind(this));
        window._py_jsobjectman.append_callback("get_type_fn", this._get_type_fn.bind(this));
        window._py_jsobjectman.append_callback("get_attr_fn", this._get_attr_fn.bind(this));
        window._py_jsobjectman.append_callback("set_attr_fn", this._set_attr_fn.bind(this));
        window._py_jsobjectman.append_callback("has_attr_fn", this._has_attr_fn.bind(this));
        window._py_jsobjectman.append_callback("del_attr_fn", this._del_attr_fn.bind(this));
        window._py_jsobjectman.append_callback("call_fn", this._call_fn.bind(this));
        window._py_jsobjectman.append_callback("call_method_fn", this._call_method_fn.bind(this));
    }

    _make_js_object(item: any){
        return new Promise((resolve: any, reject: any) => {
            window.with_uuid4((uuid: string)=>{
                this.add(uuid, item);
                resolve(uuid);
            });
        });
    }

    add(item_id: string, item: any) {
        this.storage[item_id] = item;
    }

    remove(item_id: string) {
        delete this.storage[item_id];
    }

    get (item_id: string): any {
        return this.storage[item_id];
    }

    get_type (item_id: string): any {
        return typeof this.storage[item_id];
    }

    get_list(item_ids: string[]): any[] {
        let retVal = [];

        for (let i = 0; i < item_ids.length; i++) {
            retVal.push(this.get(item_ids[i]));
        }

        return retVal;
    }

    get_pairs(item_ids: any): any {
        let retVal: ObjectStorage = {};

        for (const [key, value] of Object.entries(item_ids)) {
            // Looking up both keys AND values from stored objects:
            retVal[this.get(key)] = this.get(<string>value);
        }

        return retVal;
    }

    access(item_id: string, access_code: string, args: any = {}, obj_param: string = "obj") {
        if ((typeof args) === "string") {
            // Assume Python gave us a JsObject instead of a dict.
            // In which case, look of the JsObject
            args = this.get(args);
        }

        let arg_keys = ["id", obj_param]
        let arg_values = [this.get.bind(this), this.storage[item_id]]

        for (const [key, value] of Object.entries(args)) {
            // console.log(`${key}: ${value}`);
            arg_keys.push(key);
            arg_values.push(value);
        }
        arg_keys.push(access_code);

        return Function(...arg_keys).bind(this)(...arg_values);
    }

    get_attr (item_id: string, attr_name: string): any {
        return this.storage[item_id][attr_name];
    }

    set_attr (item_id: string, attr_name: string, value: any): any {
        this.storage[item_id][attr_name] = this.get(value);
    }

    has_attr (item_id: string, attr_name: string) {
        return attr_name in this.storage[item_id];
    }
    
    del_attr (item_id: string, attr_name: string) {
        delete this.storage[item_id][attr_name];
    }

    call(item_id: string, args: string) {
        return this.storage[item_id](...this.get(args));
    }

    call_method(item_id: string, method_name: string, args: string) {
        return this.storage[item_id][method_name].bind(this.storage[item_id])(...this.get(args));
    }

    _JsCall_error(callback: Function, error: any, code: string = "") {
        if (this.callback_errors) {
            callback(null, {
                fn_code: code,
                name: error.name,
                message: error.name,
                stack: error.stack,
            });
        }
        else {
            callback(null, null);
            console.log(error);
            // throw error;
        }
    }

    // Callbacks to pass to Python:
    _fadd_fn(item_id: string, collect_code: string, args: any, callback: Function) {
        if ((typeof args) === "string") {
            // Assume Python gave us a JsObject instead of a dict.
            // In which case, look of the JsObject
            args = this.get(args);
        }

        let arg_keys = ["id"];
        let arg_values = [this.get.bind(this)];

        for (const [key, value] of Object.entries(args)) {
            // console.log(`${key}: ${value}`);
            arg_keys.push(key);
            arg_values.push(<any>value);
        }
        arg_keys.push(collect_code);

        let item = Function(...arg_keys).bind(this)(...arg_values);
        this._add_fn(item_id, item, callback);
    }

    _add_fn(item_id: string, item: any, callback: Function) {
        this.add(item_id, item);
        callback(null, null);
    }

    _remove_fn(item_id: any, callback: Function) {
        this.remove(item_id);
        callback();
    }
    
    _access_fn(item_id: any, access_code: string, args: any, obj_param: string, callback: Function) {
        try {
            let result = this.access(item_id, access_code, args, obj_param);
            window.with_uuid4((uuid: string) => {
                this.add(uuid, result);
                callback(uuid, null);
            });
        } catch (error: any) {
            this._JsCall_error(callback, error, access_code);
        }
    }

    _py_fn(item_id: any, callback: Function) {
        try {
            callback(this.get(item_id), null);
        } catch (error: any) {
            this._JsCall_error(callback, error);
        }
       
    }

    _get_type_fn(item_id: any, callback: Function) {
        try {
            callback(this.get_type(item_id), null);
        } catch (error: any) {
            this._JsCall_error(callback, error);
        }
       
    }

    _get_attr_fn(item_id: any, attr_name: string, callback: Function) {
        try {
            let result = this.get_attr(item_id, attr_name);
            window.with_uuid4((uuid: string) => {
                this.add(uuid, result);
                callback(uuid, null);
            });
        } catch (error: any) {
            this._JsCall_error(callback, error);
        }
        
    }

    _set_attr_fn(item_id: any, attr_name: string, value: any, callback: Function) {
        try {
            this.set_attr(item_id, attr_name, value);
            callback(null, null);

        } catch (error: any) {
            this._JsCall_error(callback, error);
        }
        
    }

    _has_attr_fn(item_id: any, attr_name: string, callback: Function) {
        try {
            let result = this.has_attr(item_id, attr_name);
            callback(result, null);
        } catch (error: any) {
            this._JsCall_error(callback, error);
        }    
    }

    _del_attr_fn(item_id: any, attr_name: string, callback: Function) {
        try {
            let result = this.del_attr(item_id, attr_name);
            callback(result, null);
        } catch (error: any) {
            this._JsCall_error(callback, error);
        }    
    }

    _call_fn(item_id: any, args: string, callback: Function) {
        try {
            // console.log(args);
            let result = this.call(item_id, args);
            window.with_uuid4((uuid: string) => {
                this.add(uuid, result);
                callback(uuid, null);
            });
        } catch (error: any) {
            this._JsCall_error(callback, error);
        }
        
    }
    _call_method_fn(item_id: any, method_name: string, args: string, callback: Function) {
        try {
            let result = this.call_method(item_id, method_name, args);
            window.with_uuid4((uuid: string) => {
                this.add(uuid, result);
                callback(uuid, null);
            });

        } catch (error: any) {
            this._JsCall_error(callback, error);
        }
        
    }
}

window._jsobjectman = new JsObjectManager();

function JsObject(item: any) {
    return window._jsobjectman._make_js_object(item);
}

window._py_jsobjectman.ready();