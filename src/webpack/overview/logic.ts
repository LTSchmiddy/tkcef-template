
import { tunnel_log_tab } from '../main';
import './styles.scss';

import * as utils from "../utils";

export let tunnel_btn: JQuery<HTMLElement> = null;

export function on_tunnel_button_click() {
    window.tunnel.check((running: boolean)=>{
        if (running) {
            window.tunnel.stop();
        } else {
            window.tunnel.start();
        }
    });
}

export function on_tunnel_start(data: string) {
    tunnel_btn.get()[0].innerText = "Stop Tunnel";
    console.log("tunnel started");
}

export function on_tunnel_stop(data: string) {
    tunnel_btn.text("Start Tunnel");
}


export function init() {
    tunnel_btn = $("#tunnel-control-btn");

    window.tunnel.add_callback('on_start', on_tunnel_start);
    window.tunnel.add_callback('on_stop', on_tunnel_stop);

    utils.bindToWindow("on_tunnel_start", on_tunnel_start);
    utils.bindToWindow("on_tunnel_stop", on_tunnel_stop);
    utils.bindToWindow("on_tunnel_button_click", on_tunnel_button_click);
}

