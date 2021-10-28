interface _Py_PyScopeManager {
    make_w_args: Function;
    make_w_kwargs: Function;
    create: Function;
    destroy: Function;
    exec: Function;
    w_exec_runner: Function;
    w_exec: Function;
    do_func: Function;
    w_do_func_runner: Function;
    w_do_func: Function;
    make_func: Function;
    get_var: Function;
    has_var: Function;
    del_var: Function;
    set_var: Function;
    raw_call_runner: Function;
    raw_call: Function;
    w_call_runner: Function;
    w_call: Function;
}

interface _Py_JsObjectManager {
    append_callback: Function;
    ready: Function;
}

interface Window {
    // Public: 
    app_manager_key: string;
    app_scope_key: string;
    with_uuid4: Function;
    py_print: Function;
    queue_update_action: Function

    // Private:
    // Python Based:
    _py_scopeman: _Py_PyScopeManager;
    _py_jsobjectman: _Py_JsObjectManager;
    _app_callbacks: any;
    _promise_load_asset_as_data_url: Function;

    _scopeman: _PyScopeManager;
    _jsobjectman: JsObjectManager;
}