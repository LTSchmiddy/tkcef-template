// Importing Bootstrap:
import { Tooltip, Toast, Popover } from 'bootstrap';

// Importing style:
import './global_style/main.scss';


import { ViewDef } from './view_def';
import * as utils from './utils';

import * as overview from "./overview/logic";

export let root: HTMLElement = document.getElementById("page-root");

export let overview_tab: ViewDef = null;
export let tunnel_log_tab: ViewDef = null;

export let tabs: ViewDef[];

export function load() {
    window.templates.get_page_root((html: string) => {
        root.innerHTML = html;
        
        overview_tab = new ViewDef(
            "overview",
            $("#overview-tab-button"),
            $("#overview-tab"),
        );

        tunnel_log_tab = new ViewDef(
            "tunnel_log",
            $("#tunnel-log-tab-button"),
            $("#tunnel-log-tab"),
        );

        tabs = [
            overview_tab,
            tunnel_log_tab
        ];

        set_view("overview");
    });
}
function set_view(name: string) {
    for (let i = 0; i < tabs.length; i++) {
        if (tabs[i].name === name) {
            tabs[i].activate();
        } else {
            tabs[i].deactivate();
        }
    }
}

load();
overview.init();

utils.bindToWindow("set_view", set_view);
