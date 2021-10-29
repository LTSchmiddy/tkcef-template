from cefpython3 import cefpython as cef
import ctypes
import tkinter as tk
import sys
import os
import time
import platform
import urllib
import logging as _logging

from . import AppFrame, webapp, logger, IMAGE_EXT, MAC, WINDOWS, LINUX
from .webframe import WebAppBrowserFrame


class LifespanHandler(object):
    def __init__(self, tkFrame):
        self.tkFrame = tkFrame

    def OnBeforeClose(self, browser, **_):
        logger.debug("LifespanHandler.OnBeforeClose")
        self.tkFrame.quit()


class LoadHandler(object):
    def __init__(self, browser_frame):
        self.browser_frame: WebAppBrowserFrame = browser_frame

    def OnLoadStart(self, browser, **_):
        if self.browser_frame.master.navigation_bar:
            self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())

    def OnLoadEnd(self, browser: cef.PyBrowser, frame: cef.PyFrame, http_code: int):
        print("CALLING ON_LOAD...")
        self.browser_frame.webframe.app._on_page_loaded(browser, frame, http_code)


class FocusHandler(object):
    """For focus problems see Issue #255 and Issue #535."""

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnTakeFocus(self, next_component, **_):
        logger.debug(
            "FocusHandler.OnTakeFocus, next={next}".format(next=next_component)
        )

    def OnSetFocus(self, source, **_):
        logger.debug("FocusHandler.OnSetFocus, source={source}".format(source=source))
        if LINUX:
            return False
        else:
            return True

    def OnGotFocus(self, **_):
        logger.debug("FocusHandler.OnGotFocus")
        if LINUX:
            self.browser_frame.focus_set()



# class RequestHandler(object):
#     def __init__(self):
#         self.response_handler = ResponseHandler()
    
#     def GetResourceHandler(self, browser: cef.PyBrowser, frame: cef.PyFrame, request: cef.Request):
#         # logger.debug(f"{browser=}")
#         # logger.debug(f"{frame=}")
#         # logger.debug(f"{request=}")
#         url_str = request.GetUrl()
#         url = urllib.parse.urlparse(url_str)
#         print(f'{url=}')
#         print(f'{url_str=}')
        
#         if url.scheme == "chrome":  
#             self.response_handler = ResponseHandler()
#             return self.response_handler
        
#         return None
        

    
# class ResponseHandler(object):
#     data = b"HELLO ALEX"
    
#     def ProcessRequest(self, request: cef.Request, callback: cef.PyCallback):
#         print("Calling ProcessRequest....")
        
#         self.url_str = request.GetUrl()
#         self.url = urllib.parse.urlparse(self.url_str)
        
#         if self.url.scheme == "local":
#             return False
        
#         callback.Continue()
#         return True
    
#     def GetResponseHeaders(self, response: cef.PyResponse, response_length_out: list[int], redirect_url_out: list[str]):
#         # response.
#         response_length_out[0] = len(self.data)
    
#     def ReadResponse(self, data_out: list[bytes], bytes_to_read: int, bytes_read_out: list[int], callback: cef.PyCallback):
#         data_out.append(self.data[:bytes_to_read]);
        
#         bytes_read_out[0] = bytes_to_read
        
#         print("Calling ReadResponse....")
        
#         callback.Continue()
#         return True
    
#     def CanGetCookie(self, cookie: cef.Cookie):
#         return False
    
#     def CanSetCookie(self, cookie: cef.Cookie):
#         return False
    
#     def Cancel(self):
#         pass