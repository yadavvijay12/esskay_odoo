/** @odoo-module **/
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";

export const webNotificationService = {
    dependencies: ["action", "bus_service", "notification", "rpc"],

    start(env, {bus_service, notification}) {
        let webNotifTimeouts = {};
        function _handleNotificationSuccessNotification(notifications) {
            console.log("testtt111");
            Object.values(webNotifTimeouts).forEach((notifications) =>
                browser.clearTimeout(notifications)
            );
            webNotifTimeouts = {};
                browser.setTimeout(function () {
                    notification.add(notifications.message, {
                        title: notifications.title,
                        type: "success",
                        sticky: notifications.sticky,
                        className: notifications.className,
                    });
                });
        }

        bus_service.addEventListener('notification', ({ detail: notifications }) => {
            for (const { payload, type } of notifications) {
                console.log(payload, "paylodaadddddd");
                if (type === "success_notify") {
                    _handleNotificationSuccessNotification(payload);
                }
            }
        });
    },
};

registry.category("services").add("webNotification", webNotificationService);
