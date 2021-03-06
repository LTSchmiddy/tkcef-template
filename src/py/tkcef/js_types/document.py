from ..js_object import JsObject


class JsDocument(JsObject):

    # Properties
    activeElement: JsObject
    alinkColor: JsObject
    all: JsObject
    anchors: JsObject
    applets: JsObject
    bgColor: JsObject
    body: JsObject
    characterSet: JsObject
    childElementCount: JsObject
    children: JsObject
    compatMode: JsObject
    contentType: JsObject
    currentScript: JsObject
    defaultView: JsObject
    designMode: JsObject
    dir: JsObject
    doctype: JsObject
    documentElement: JsObject
    documentURI: JsObject
    domain: JsObject
    embeds: JsObject
    fgColor: JsObject
    firstElementChild: JsObject
    forms: JsObject
    fullscreen: JsObject
    fullscreenElement: JsObject
    fullscreenEnabled: JsObject
    head: JsObject
    height: JsObject
    hidden: JsObject
    images: JsObject
    implementation: JsObject
    lastElementChild: JsObject
    lastModified: JsObject
    lastStyleSheetSet: JsObject
    linkColor: JsObject
    links: JsObject
    location: JsObject
    mozSyntheticDocument: JsObject
    onafterscriptexecute: JsObject
    onbeforescriptexecute: JsObject
    onfullscreenchange: JsObject
    onfullscreenerror: JsObject
    onoffline: JsObject
    ononline: JsObject
    onvisibilitychange: JsObject
    origin: JsObject
    pictureInPictureElement: JsObject
    pictureInPictureEnabled: JsObject
    plugins: JsObject
    pointerLockElement: JsObject
    preferredStyleSheetSet: JsObject
    readyState: JsObject
    referrer: JsObject
    rootElement: JsObject
    scripts: JsObject
    scrollingElement: JsObject
    selectedStyleSheetSet: JsObject
    styleSheets: JsObject
    styleSheetSets: JsObject
    timeline: JsObject
    title: JsObject
    URL: JsObject
    visibilityState: JsObject
    vlinkColor: JsObject
    width: JsObject
    xmlEncoding: JsObject
    xmlVersion: JsObject

    # Methods:
    # adoptNode: JsObject
    # append: JsObject
    # caretPositionFromPoint: JsObject
    # caretRangeFromPoint: JsObject
    # clear: JsObject
    # close: JsObject
    # createAttribute: JsObject
    # createCDATASection: JsObject
    # createComment: JsObject
    # createDocumentFragment: JsObject
    # createElement: JsObject
    # createElementNS: JsObject
    # createEntityReference: JsObject
    # createEvent: JsObject
    # createExpression: JsObject
    # createNodeIterator: JsObject
    # createNSResolver: JsObject
    # createProcessingInstruction: JsObject
    # createRange: JsObject
    # createTextNode: JsObject
    # createTouch: JsObject
    # createTouchList: JsObject
    # createTreeWalker: JsObject
    # elementFromPoint: JsObject
    # elementsFromPoint: JsObject
    # enableStyleSheetsForSet: JsObject
    # evaluate: JsObject
    # execCommand: JsObject
    # exitFullscreen: JsObject
    # exitPictureInPicture: JsObject
    # exitPointerLock: JsObject
    # getAnimations: JsObject
    # getBoxObjectFor: JsObject
    # getElementById: JsObject
    # getElementsByClassName: JsObject
    # getElementsByName: JsObject
    # getElementsByTagName: JsObject
    # getElementsByTagNameNS: JsObject
    # getSelection: JsObject
    # hasFocus: JsObject
    # hasStorageAccess: JsObject
    # importNode: JsObject
    # mozSetImageElement: JsObject
    # open: JsObject
    # prepend: JsObject
    # queryCommandEnabled: JsObject
    # queryCommandSupported: JsObject
    # querySelector: JsObject
    # querySelectorAll: JsObject
    # registerElement: JsObject
    # releaseCapture: JsObject
    # replaceChildren: JsObject
    # requestStorageAccess: JsObject
    # write: JsObject
    # writeln: JsObject

    # Events:
    animationcancel: JsObject
    animationend: JsObject
    animationiteration: JsObject
    animationstart: JsObject
    copy: JsObject
    cut: JsObject
    DOMContentLoaded: JsObject
    drag: JsObject
    dragend: JsObject
    dragenter: JsObject
    dragleave: JsObject
    dragover: JsObject
    dragstart: JsObject
    drop: JsObject
    fullscreenchange: JsObject
    fullscreenerror: JsObject
    gotpointercapture: JsObject
    keydown: JsObject
    keypress: JsObject
    keyup: JsObject
    lostpointercapture: JsObject
    paste: JsObject
    pointercancel: JsObject
    pointerdown: JsObject
    pointerenter: JsObject
    pointerleave: JsObject
    pointerlockchange: JsObject
    pointerlockerror: JsObject
    pointermove: JsObject
    pointerout: JsObject
    pointerover: JsObject
    pointerup: JsObject
    readystatechange: JsObject
    scroll: JsObject
    selectionchange: JsObject
    selectstart: JsObject
    touchcancel: JsObject
    touchend: JsObject
    touchmove: JsObject
    touchstart: JsObject
    transitioncancel: JsObject
    transitionend: JsObject
    transitionrun: JsObject
    transitionstart: JsObject
    visibilitychange: JsObject
    wheel: JsObject
    Node: JsObject
    EventTarget: JsObject

    def get_element(self, query: str) -> JsObject:
        return self.manager.from_func(
            "return document.querySelector(query);", {"query": query}
        )

    def get_elements(self, query: str) -> JsObject:
        return self.manager.from_func(
            "return document.querySelectorAll(query);", {"query": query}
        )

    def get_element_list(self, query: str) -> JsObject:
        result = self.get_elements(query)
        retVal = []

        for i in range(0, result["length"].py()):
            retVal.append(result[i])

        return retVal

    def htmlToElement(self, html: str):
        template = self.access("return self.createElement('template')")
        template["innerHTML"] = html.strip()
        return template["content"]["firstChild"]
