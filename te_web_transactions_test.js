// Import required libraries
const assert = require('assert');

// Step 1: Fetch the URL and parse the JSON response
const url = 'https://testapp.net/ht/?format=json';
test.open(url);

// Wait for the response to load
test.wait(5000);

// Get the raw JSON response
let jsonResponse = test.getHtml();
let data;

// Parse the JSON response
try {
    data = JSON.parse(jsonResponse);
} catch (e) {
    test.fail('Failed to parse JSON response: ' + e.message);
}

// Step 2: Define components to check
const components = ['database', 'cyberark', 'infoblox', 'Redis'];

// Check the status of each component
let failedComponents = [];
components.forEach(component => {
    if (data[component] !== 'working') {
        failedComponents.push(component);
    }
});

// Step 3: Assert all components are 'working'
if (failedComponents.length > 0) {
    test.fail('The following components are not working: ' + failedComponents.join(', '));
} else {
    test.log('All components are working as expected.');
}

// Complete the test
test.done();
