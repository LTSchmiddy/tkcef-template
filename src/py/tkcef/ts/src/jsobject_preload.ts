interface ObjectStorage {
    [key: string]: any;
}

class JsObjectManager {
    storage: ObjectStorage;
    
    constructor() {
        this.storage = {};
    }
}

window._jsobjectman = new JsObjectManager();