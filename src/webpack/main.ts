// Importing Bootstrap:
import { Tooltip, Toast, Popover } from 'bootstrap';

// Importing style:
import './global_style/main.scss';


import { ViewDef } from './view_def';
import * as utils from './utils';

const exports: any = {}

export function generatePyClassHints(item: any): string {
    return generatePyClassHintsFromArray(Object.getOwnPropertyNames(item));
}

export function generatePyClassHintsFromArray(array: any[]): string {
    let retVal = "";

    array.forEach((i, index)=>{
        retVal += `${i}: JsObject\n`;
    });


    return retVal;
}

export let root: HTMLElement = document.getElementById("page-root");


