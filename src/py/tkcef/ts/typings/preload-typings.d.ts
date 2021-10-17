interface Window {
    // Public: 
    app_manager_key: string;
    app_scope_key: string;
    templates: any;
    with_uuid4: Function;

    // Private:
    _pyscopeman: any;
    _py_jsobjectman: any;
    _app_callbacks: any;
    _handle_py_func: Function;

    _scopeman: PyScopeManager;
    _jsobjectman: JsObjectManager;
}