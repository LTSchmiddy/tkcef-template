"use strict";
class JsObjectManager {
    constructor() {
        this.storage = {};
        this.callback_errors = false;
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
    _make_js_object(item) {
        return new Promise((resolve, reject) => {
            window.with_uuid4((uuid) => {
                this.add(uuid, item);
                resolve(uuid);
            });
        });
    }
    add(item_id, item) {
        this.storage[item_id] = item;
    }
    remove(item_id) {
        delete this.storage[item_id];
    }
    get(item_id) {
        return this.storage[item_id];
    }
    get_type(item_id) {
        return typeof this.storage[item_id];
    }
    get_list(item_ids) {
        let retVal = [];
        for (let i = 0; i < item_ids.length; i++) {
            retVal.push(this.get(item_ids[i]));
        }
        return retVal;
    }
    get_pairs(item_ids) {
        let retVal = {};
        for (const [key, value] of Object.entries(item_ids)) {
            // Looking up both keys AND values from stored objects:
            retVal[this.get(key)] = this.get(value);
        }
        return retVal;
    }
    access(item_id, access_code, args = {}, obj_param = "self") {
        if ((typeof args) === "string") {
            // Assume Python gave us a JsObject instead of a dict.
            // In which case, look of the JsObject
            args = this.get(args);
        }
        let arg_keys = ["id", obj_param];
        let arg_values = [this.get.bind(this), this.storage[item_id]];
        for (const [key, value] of Object.entries(args)) {
            // console.log(`${key}: ${value}`);
            arg_keys.push(key);
            arg_values.push(value);
        }
        arg_keys.push(access_code);
        return Function(...arg_keys).bind(this)(...arg_values);
    }
    get_attr(item_id, attr_name) {
        return this.storage[item_id][attr_name];
    }
    set_attr(item_id, attr_name, value) {
        this.storage[item_id][attr_name] = this.get(value);
    }
    has_attr(item_id, attr_name) {
        return attr_name in this.storage[item_id];
    }
    del_attr(item_id, attr_name) {
        delete this.storage[item_id][attr_name];
    }
    call(item_id, args) {
        return this.storage[item_id](...this.get(args));
    }
    call_method(item_id, method_name, args) {
        return this.storage[item_id][method_name].bind(this.storage[item_id])(...this.get(args));
        // console.log();
        // return this.access(item_id, `return self.${method_name}(..._args)`, {_args: args});
    }
    _JsCall_error(callback, error, code = "") {
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
    _fadd_fn(item_id, collect_code, args, callback) {
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
            arg_values.push(value);
        }
        arg_keys.push(collect_code);
        let item = Function(...arg_keys).bind(this)(...arg_values);
        this._add_fn(item_id, item, callback);
    }
    _add_fn(item_id, item, callback) {
        this.add(item_id, item);
        callback(null, null);
    }
    _remove_fn(item_id, callback) {
        this.remove(item_id);
        callback();
    }
    _access_fn(item_id, access_code, args, obj_param, callback) {
        try {
            let result = this.access(item_id, access_code, args, obj_param);
            window.with_uuid4((uuid) => {
                this.add(uuid, result);
                callback(uuid, null);
            });
        }
        catch (error) {
            this._JsCall_error(callback, error, access_code);
        }
    }
    _py_fn(item_id, callback) {
        try {
            callback(this.get(item_id), null);
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
    _get_type_fn(item_id, callback) {
        try {
            callback(this.get_type(item_id), null);
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
    _get_attr_fn(item_id, attr_name, callback) {
        try {
            let result = this.get_attr(item_id, attr_name);
            window.with_uuid4((uuid) => {
                this.add(uuid, result);
                callback(uuid, null);
            });
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
    _set_attr_fn(item_id, attr_name, value, callback) {
        try {
            this.set_attr(item_id, attr_name, value);
            callback(null, null);
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
    _has_attr_fn(item_id, attr_name, callback) {
        try {
            let result = this.has_attr(item_id, attr_name);
            callback(result, null);
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
    _del_attr_fn(item_id, attr_name, callback) {
        try {
            let result = this.del_attr(item_id, attr_name);
            callback(result, null);
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
    _call_fn(item_id, args, callback) {
        try {
            // console.log(args);
            let result = this.call(item_id, args);
            window.with_uuid4((uuid) => {
                this.add(uuid, result);
                callback(uuid, null);
            });
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
    _call_method_fn(item_id, method_name, args, callback) {
        try {
            let result = this.call_method(item_id, method_name, args);
            window.with_uuid4((uuid) => {
                this.add(uuid, result);
                callback(uuid, null);
            });
        }
        catch (error) {
            this._JsCall_error(callback, error);
        }
    }
}
window._jsobjectman = new JsObjectManager();
function JsObject(item) {
    return window._jsobjectman._make_js_object(item);
}
window._py_jsobjectman.ready();
//# sourceMappingURL=jsobject_preload.js.map