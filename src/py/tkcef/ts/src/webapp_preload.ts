// This code is loaded before the page HTML is loaded:

function _load_page_content(page_code: string) {
    document.open();
    document.write(page_code);

    document.close();
}

