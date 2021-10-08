
export class ViewDef {
    _active: boolean;

    name: string;

    button: JQuery<HTMLElement>;
    viewport: JQuery<HTMLElement>;
    
    constructor(p_name: string, p_button: JQuery<HTMLElement>, p_viewport: JQuery<HTMLElement>) {
        this._active = false;

        this.name = p_name;

        this.button = p_button;
        this.viewport = p_viewport;
    }

    activate() {
        this.button.addClass("btn-secondary");
        this.button.removeClass("btn-outline-secondary");
        this.viewport.show();

        this._active = true;
    }

    deactivate() {
        this.button.addClass("btn-outline-secondary");
        this.button.removeClass("btn-secondary");
        this.viewport.hide();

        this._active = false;
    }

    set_active(value: boolean) {
        if (!this._active && value) {
            this.activate();

        } else if (this._active && !value) {
            this.deactivate();
        }
    }

    get_active(): boolean {
        
        return this._active;
    }
}