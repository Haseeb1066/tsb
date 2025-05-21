async function applyFilter() {
  await tableau.extensions.initializeAsync();

  let dashboard = tableau.extensions.dashboardContent.dashboard;
  let worksheet = dashboard.worksheets[0]; // Use the correct worksheet index or name
  let inputText = document.getElementById('userInput').value;

  worksheet.applyFilterAsync(
    'Year', // Replace with actual filter field name
    inputText,
    tableau.FilterUpdateType.REPLACE
  );
}
