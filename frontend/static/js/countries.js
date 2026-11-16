import TomSelect from "tom-select";
import "tom-select/dist/css/tom-select.default.css";

export async function renderCountries(selectorID) {
  const res = await fetch(`${window.location.origin}/api/locations`);
  const locations = await res.json();
  const options = locations.flatMap((country) => [
    {
      value: country.code,
      text: country.name,
      searchText: `${country.name} ${country.code}`,
      depth: 0,
    },
    ...(country.subdivisions || []).map((sub) => ({
      value: `${country.code}:${sub.code}`,
      text: sub.name,
      parentName: country.name,
      searchText: `${country.name} ${country.code} ${sub.name} ${sub.code}`,
      depth: 1,
    })),
  ]);
  return new TomSelect(`#${selectorID}`, {
    options,
    searchField: ["searchText"],
    placeholder: "Type to search...",
    render: {
      option: function (data, escape) {
        const indent = data.depth * 8;
        const fontWeight = data.depth === 0 ? "font-weight: 600;" : "";
        return `<div style="padding-left: ${indent + 8}px; ${fontWeight}">${escape(data.text)}</div>`;
      },
      item: function (data, escape) {
        // Shows "Country > Subdivision" in the input box once selected
        const label = data.parentName
          ? `${data.parentName} › ${data.text}`
          : data.text;
        return `<div>${escape(label)}</div>`;
      },
    },
  });
}
