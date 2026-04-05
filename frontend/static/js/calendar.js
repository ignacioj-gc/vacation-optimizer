import { Calendar } from "vanilla-calendar-pro";
import 'vanilla-calendar-pro/styles/index.css';
import { getDate, parseDates, getDateString } from 'vanilla-calendar-pro/utils';

export async function loadCalendar(userLocale, year) {
    const holidayList = await loadHolidays(userLocale, year);
    console.log(holidayList);
    console.log(holidayList.keys)

    let cal = new Calendar("#calendar", {
        firstWeekday: 0,
        disableWeekdays: [0,6],
        type: 'multiple',
        displayMonthsCount: 12,
        selectionDatesMode: 'multiple',
        selectionYearsMode: false,
        selectionMonthsMode: false,
        locale: userLocale,
        selectedYear: year,
        dateMin: `${year}-01-01`,
        dateMax: `${year}-12-31`,
    })
    cal.selectedDates = Object.keys(holidayList)
    cal.init()
}

async function loadHolidays(userLocale, year) {
    const userCountry = userLocale.split('-')[1];
    const requestData = {
        country: userCountry,
        year: year
    }
    const holidays = await fetch(`${window.location.origin}/api/get_holidays`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    });
    return holidays.json()
}