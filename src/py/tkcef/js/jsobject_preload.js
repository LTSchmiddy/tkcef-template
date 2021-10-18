"use strict";
class JsObjectManager {
    constructor() {
        this.storage = {};
        window._py_jsobjectman.append_callback("fadd_fn", this._fadd_fn.bind(this));
        window._py_jsobjectman.append_callback("add_fn", this._add_fn.bind(this));
        window._py_jsobjectman.append_callback("remove_fn", this._remove_fn.bind(this));
    }
    add(item_id, item) {
        this.storage[item_id] = item;
    }
    remove(item_id) {
        delete this.storage[item_id];
    }
    // Callbacks to pass to Python:
    _fadd_fn(item_id, collect_code, callback) {
        let item = Function(collect_code)();
        this._add_fn(item_id, item, callback);
    }
    _add_fn(item_id, item, callback) {
        this.add(item_id, item);
        callback();
    }
    _remove_fn(item_id, callback) {
        this.remove(item_id);
        callback();
    }
}
window._jsobjectman = new JsObjectManager();
window._py_jsobjectman.ready();
//# sourceMappingURL=jsobject_preload.js.map