/// <reference types="jquery"
/// <reference types="jqueryui"
/// <reference types="datatables.net"

const { loadCalendar } = require("./ calendar");

const userLocale = navigator.language || 'en-PR'
console.log(`User locale obtained: ${userLocale}`)

async function loadHolidays() {
    let year = $("#year");
    const response = await fetch(window + "/api/get_holidays");
    return response;
};

function displayVacationDates() {
    let vacations;
}

document.addEventListener('DOMContentLoaded', () => {
    loadCalendar(userLocale)
});