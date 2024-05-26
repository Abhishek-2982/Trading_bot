// // script.js
// function fetchData() {
//     $.ajax({
//         url: '/taapi_data/',
//         type: 'GET',
//         dataType: 'json',
//         success: function(data) {
//             // Update HTML with new data
//             $('#data-container').html('<pre>' + JSON.stringify(data, null, 2) + '</pre>');
//         },
//         complete: function() {
//             // Schedule the next fetch after 15 seconds
//             setTimeout(fetchData, 15000);
//         }
//     });
// }

// $(document).ready(function() {
//     // Initial fetch
//     fetchData();
// });
