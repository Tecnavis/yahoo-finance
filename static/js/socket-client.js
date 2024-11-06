const socket = io(); // Adjust if necessary for your server's URL

socket.on('connect', () => {
    console.log('Connected to the server');
});

socket.on('currency_update', (data) => {
    console.log(data);
    document.getElementById('currency-data').innerHTML = `
        <p>Currency: ${data.currency}</p>
        <p>Current Rate: ${data.current_rate}</p>
        <p>Today's High: ${data.today_high}</p>
        <p>Today's Low: ${data.today_low}</p>
        <p>Date: ${data.today}</p>
    `;
});
