"use strict";
// This code is loaded before the page HTML is loaded:
function _load_page_content(page_code) {
    document.open();
    document.write(page_code);
    document.close();
}
function load_asset_as_data_url(path, mimetype = null) {
    return new Promise((resolve, reject) => {
        window._promise_load_asset_as_data_url(path, mimetype, resolve, reject);
    });
}
function _setup_title_updater() {
    // Call once for the current title:
    window._app_callbacks.on_js_title_change(document.title);
    // select the target node
    let target = document.querySelector('title');
    // create an observer instance
    let observer = new MutationObserver(function (mutations) {
        // We need only first event and only new value of the title
        console.log(mutations[0].target.nodeValue);
        window._app_callbacks.on_js_title_change(mutations[0].target.nodeValue);
    });
    // configuration of the observer:
    let config = { subtree: true, characterData: true, childList: true };
    // pass in the target node, as well as the observer options
    observer.observe(target, config);
}
;
_setup_title_updater();
//# sourceMappingURL=webapp_preload.js.map