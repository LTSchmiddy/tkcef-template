
/**
 * @param {String} HTML representing a single element
 * @return {Element}
 */
export function htmlToElement(html: string) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

/**
 * @param {String} HTML representing any number of sibling elements
 * @return {NodeList} 
 */
export function htmlToElements(html: string) {
    var template = document.createElement('template');
    template.innerHTML = html;
    return template.content.childNodes;
}

// Makes it easier to access things from debug console:
export function bindToWindow(name: string, bind_object: any) {
    (<any>window)[name] = bind_object;
}
// LOL:
bindToWindow('bindToWindow', bindToWindow);

export function bWindow(): any {
    return <any>window;
}