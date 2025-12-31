/// <reference types="jquery"
/// <reference types="jqueryui"
/// <reference types="datatables.net"

import { Calendar } from "@fullcalendar/core"

function loadHolidays() {
    let year = $("#year");
    let holiday_list = fetch(window + "/api/get_holidays");
    return holiday_list
}

document.addEventListener('DOMContentLoaded', () => {
    var calendarDiv = document.getElementById("calendar");
    var calendar = new Calendar(calendarDiv, {
        initialView: 'multiMonthYear'
    });
});