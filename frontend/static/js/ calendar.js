import { Calendar } from "vanilla-calendar-pro";
import 'vanilla-calendar-pro/styles/index.css';
import { getDate, parseDates, getDateString } from 'vanilla-calendar-pro/utils';

export function loadCalendar(userLocale) {
    let cal = new Calendar("#calendar", {
        type: 'multiple',
        displayMonthsCount: 12,
        monthsToSwitch: 12,
        selectionDatesMode: 'multiple',
        locale: userLocale
    })
}