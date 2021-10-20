interface Window {
    // Public: 
    app_manager_key: string;
    app_scope_key: string;
    with_uuid4: Function;
    py_print: Function;

    // Private:
    _py_scopeman: any;
    _py_jsobjectman: any;
    _app_callbacks: any;
    _handle_py_func: Function;

    _scopeman: _PyScopeManager;
    _jsobjectman: JsObjectManager;
}