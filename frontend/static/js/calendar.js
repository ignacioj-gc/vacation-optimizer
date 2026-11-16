import { Calendar, months } from "vanilla-calendar-pro";
import "vanilla-calendar-pro/styles/index.css";
import { getDate, parseDates, getDateString } from "vanilla-calendar-pro/utils";

export async function loadCalendar(request, cal) {
  console.log(request);
  const { country, subdivision, year } = request;
  const holidayList = await loadHolidays(request);
  console.log(holidayList);

  if (cal instanceof Calendar) {
    cal.destroy();
  }
  cal = new Calendar("#calendar", {
    extensions: [months],
    firstWeekday: 0,
    disableWeekdays: [0, 6],
    type: "multiple",
    displayMonthsCount: 12,
    selectionDatesMode: "multiple",
    selectionYearsMode: false,
    selectionMonthsMode: false,
    selectedYear: Number(year),
    selectedMonth: 0,
    selectedDates: Object.keys(holidayList),
  });
  cal.init();
  return cal;
}

async function loadHolidays(request) {
  const holidays = await fetch(`${window.location.origin}/api/get_holidays`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
  return holidays.json();
}
