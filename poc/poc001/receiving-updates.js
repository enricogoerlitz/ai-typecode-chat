const axios = require('axios');

async function runFlow() {
    let currentResponse = null;
    try {
        const response = await axios({
            method: 'get',
            url: 'http://127.0.0.1:8080/run/flow',
            responseType: 'stream' // Enable streaming response
        });

        response.data.on('data', (chunk) => {
            currentResponse = JSON.parse(chunk.toString().trim());
            console.log('Current response:', currentResponse);
        });

        response.data.on('end', () => {
            console.log('Flow completed!');
            console.log("FINAL RESPONSE:", currentResponse);
        });

    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Start the client
runFlow();
