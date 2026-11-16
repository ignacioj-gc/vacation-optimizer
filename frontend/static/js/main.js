import { loadCalendar } from "./calendar";
import { renderCountries } from "./countries";
import "../css/style.css";

let cal = null;

document.addEventListener('DOMContentLoaded', () => {
    const tomselector = renderCountries('country-selection');
    const yearSelector = document.getElementById("year");
    const countrySelector = document.getElementById("country-selection");
    const vacationDaysField = document.getElementById("vacation-days")
    vacationDaysField?.setAttribute("value", "15");
    yearSelector?.setAttribute("value", new Date().getFullYear());

    const calendarLoadBtn = document.getElementById("load-calendar-btn");
    calendarLoadBtn?.addEventListener("click", () => {
        let location = countrySelector.value;
        const [country, subdivision] = location.split(':');
        let year = yearSelector.value;
        cal = loadCalendar({ country, subdivision, year}, cal);
    });
    /* Add event listener so that each time the fields are updated, the calendar holidays change.
     Decide whether we want to use built-in year selection or have that be part of the control panel.
     If the latter, disable year selection in vanilla calendar. */
    // @ts-ignore
});