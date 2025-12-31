/// <reference types="jquery"
/// <reference types="jqueryui"
/// <reference types="datatables.net"

import { Calendar } from "@fullcalendar/core"
import multiMonthPlugin from "@fullcalendar/multimonth"
import bootstrap5Plugin from "@fullcalendar/bootstrap5"

function loadHolidays() {
    let year = $("#year");
    let holiday_list = fetch(window + "/api/get_holidays");
    return holiday_list
}

document.addEventListener('DOMContentLoaded', () => {
    var calendarDiv = document.getElementById("calendar");
    var calendar = new Calendar(calendarDiv, {
        plugins: [multiMonthPlugin, bootstrap5Plugin],
        timeZone: 'AST',
        initialView: 'multiMonthYear',
        themeSystem: 'bootstrap5'
    });
    calendar.render();
});