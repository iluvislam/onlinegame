const https = require('https');
const fs = require('fs');
const dgram = require('dgram');
process.on('uncaughtException', (r) => {
console.log(r);
});
let ssoption = {
cert: "-----BEGIN CERTIFICATE-----\r\nMIIDfjCCAmagAwIBAgIUBqlXQAFmeysUkXQTTetpNqTVUu4wDQYJKoZIhvcNAQELBQAwFTETMBEGA1UEAwwKenR6cHJvZGVrajAeFw0yMjA2MTYxNjAwNTRaFw0yMzA2MTYxNjAwNTRaMBUxEzARBgNVBAMMCnp0enByb2Rla2owggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDAj6WWsIYJ1iK4G5m06JU4Ut3CpkZXYrH/VsiigfK5Aqe9zmxLk4vXq1E4qOM5H36bKLYsSEPFP9GOg2Buq36SBj77/HCwpUYzN2VK4IROXhE/6XwEWGH83Ci6pWWXo4UAlXY+I5Ze6XUds1qj3UW3kc7J60saG+OZZ1Gn2mPADmqI8twcEI1mDVlU5SbbM7TAnWdbhQpX4vlMrzEDQOskBqkfpYzl3g6GzVJn7opFFDCn/G/OOJ2GshRiFR7b4WsOABKC40ozi96PW6iDxrKRPQLxgx8UtDhxUQyYFOaBtRT2NZiUu18SlZEH7skMw+mv7cXfj+GXubCpoCMtaNZPAgMBAAGjgcUwgcIwHQYDVR0OBBYEFHADvOTQ1tQiXvE6ebKOEOF8x6AzMB8GA1UdIwQYMBaAFHADvOTQ1tQiXvE6ebKOEOF8x6AzMA8GA1UdEwEB/wQFMAMBAf8wTQYDVR0RBEYwRIIOZ3Jvd3RvcGlhMS5jb22CDmdyb3d0b3BpYTIuY29tghAqLmdyb3d0b3BpYTEuY29tghAqLmdyb3d0b3BpYTIuY29tMAsGA1UdDwQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDATANBgkqhkiG9w0BAQsFAAOCAQEABG7Bh85eTfl0bIiUwOXdzI4U3gbNDS6KNuhg98OMFr5wlGnur1x5w5zqpsxhC8C8bCiUqBuddg1APviMpX9GNpxCarig/YGGElw1LmaggY0x7YYWw0Vm1ea+R93gAVbFFHI3s0x/xx10y2SvR0DD9IzHeZ5ycBo9M8+9a2czwHeJ+zfzbPnFRc94KSPf07v7zLcoePli3TUj0qLXr/4P2K5G4Q9Vtj6wMZf0KYHGaa/RWZOKYEw3SDOiPeRSMXlx38uGIslXavJfhdlqUOG6gSZ3wv6ywIGA691tbqLRRun3U7NQ0tAgyUSmv98a5g/7Tjch+gyOKTLtiDwCvfmEyQ==\r\n-----END CERTIFICATE-----",
key : "-----BEGIN PRIVATE KEY-----\r\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDAj6WWsIYJ1iK4G5m06JU4Ut3CpkZXYrH/VsiigfK5Aqe9zmxLk4vXq1E4qOM5H36bKLYsSEPFP9GOg2Buq36SBj77/HCwpUYzN2VK4IROXhE/6XwEWGH83Ci6pWWXo4UAlXY+I5Ze6XUds1qj3UW3kc7J60saG+OZZ1Gn2mPADmqI8twcEI1mDVlU5SbbM7TAnWdbhQpX4vlMrzEDQOskBqkfpYzl3g6GzVJn7opFFDCn/G/OOJ2GshRiFR7b4WsOABKC40ozi96PW6iDxrKRPQLxgx8UtDhxUQyYFOaBtRT2NZiUu18SlZEH7skMw+mv7cXfj+GXubCpoCMtaNZPAgMBAAECggEACoQNu/P57fGWxc0kEMAe3guQdr/T2ZPXOqWHoXBNTBM8C96JBXuSSH3fmqOGfSkeJeUMRdDQeqYokIrWKlUNPXY/3E0F7m+oLMXar0MhlpIGiSH8FtSozUFMrBy6NpTEf6qp4WzaGmbPcYbI7Wf5FbRNwbMqz8s0G72LtQn1JpjKkm1whmFEN9OTDikLLBzp/AAxXkIC+8HytH5x0DMtUnHJbNLry2p/oOyzWO/JgB0C7+3FDd6ddJnzTn2J3bPP+Nnb8B0MRaThvP6gNfFP94hoSTe/onfEMdnSd16IX4GanyNv8oI08EH4+OVpAeyUz+BDqqZNjgFGLA/C8dqWKQKBgQD1yviPqbnlWMrjJecWM3N39FccR6KtNtTDi6AVBQLPzo7w92EwJSCaogf2j7//bgOIABlJYIecKMIF6YD7FpuzN296PHeXml3Ax90uFVt+ekDTmCeTR08Z4PVDvuhajmrbDbm6m+1z6STRAJGmAyC9Bn3GuAVLtHYw9RPhHe4TiwKBgQDIjsSn328l3RB4xw39+aUMvKsxgoLtfWdNHL9nn8EcATMPvGCkr7IBRmIzdPZcfzEOuyY+s9AY0BFlNBDJxUubUokZdQ7l1a6gHN90vWuRTWQzPQenZZQjPZlZCStrsDKvKVsZ2FHI8CcPOFVY3+TtiogibJGCVqayLiadpO+QzQKBgQCynl/ntwX6334BeGfowFcnUw+C46QakIAp4uvgmpWigo9qGbwtCq4Y8asryOdULpSuXrQBmP6zwwLM3RX4YkOgB6chg5O9PlbnY9ceSDMHRLybiDUqWGXpfot+QdwFAv4wVlckf3AeDc3NfMZbiGZgN7lrkgt3KpvBlDhwHhoHZQKBgQCPnoU/PeanM6Y/BzSC4koKU/U38CD4Fqxp8SMz/pfYCRfatehzJooPFaru9FwTotWrmeNqVXO4wQ8j7OP0yX86DCG3hDcV6S4y5Fo0jAzCsawGcTbQ7hHmJo9wzfs1E6lH/BKL8HeosCkYYhvkF/klDeYs2JhewNSAlkH69AjGJQKBgHHlj5i3zs/knX1CRah81IzQ4NjqdJjzbQ7VPO8AjEt4RRNKEVBZDXD8t22oRAD3/YlOfgPNA8CUtaoMZXYt9bvQHpmlzzNaUpTyOXGqgI4RR+2o7aIlSBpKzvTgHhp2Cuzv1zWL7TshB06JSQuZ73whfRg+s50OK40A4ruOVniX\r\n-----END PRIVATE KEY-----"
}
let data;
https.createServer(ssoption, (req, res) => {
console.log(`INFO: ${req.connection.remoteAddress} ${req.method} to ${req.url}`);
if(req.url === "/") {
res.writeHead(302, {
'Location': '/main'
});
res.end();
return;
}else if (req.url === '/canvasjs.min.js') {
fs.readFile('cavs.js', 'utf8', (err, data) => {
res.end(data);
});
}else if (req.url === '/server/state') {
res.writeHead(200, { 'Content-Type': 'text/html' });
res.end(data);
}else if (req.url === '/main') {
res.writeHead(200, { 'Content-Type': 'text/html' });
res.write(`<!DOCTYPE html>
<html>
<head>
  <title>JSON Data</title>
  <style>
    body { background-color: black; color: white; font-family: Arial, sans-serif; margin: 0; padding: 0; }
    h1 { background-color: #333; color: white; padding: 10px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { padding: 10px; text-align: left; border: 1px solid #555; }
    th { background-color: #333; color: white; }
    tr:nth-child(even) { background-color: #555; }
  </style>
</head>
<body>
  <table id="graph">
    <tr>
      <div id="chartContainer" style="height: 400px; width: 100%;"></div>
      <div id="dpschartContainer" style="height: 400px; width: 100%;"></div>
    </tr>
  </table>
  <h1>Players Map (<span id="players-size"></span>)</h1>
  <table id="players-table">
    <!-- Players Map table content -->
  </table>
  <h1>Clients Map (<span id="clients-size"></span>)</h1>
  <table id="clients-table">
    <!-- Clients Map table content -->
  </table>

  <h1>Worlds Map (<span id="worlds-size"></span>)</h1>
  <table id="worlds-table">
    <!-- Worlds Map table content -->
  </table>

  <script src="https://127.0.0.1/canvasjs.min.js"></script>
  <script>
    // Function to fetch data from the /server/state endpoint and update the tables
    let dpsPacket = [];
    let dpsData = [];
    let xVal = 0;
    let dpsxVal = 0;
let dpschart = new CanvasJS.Chart("dpschartContainer", {
  backgroundColor: "black",
  title: {
    text: "Live DPS",
    fontColor: "white"
  },
  axisX: {
    title: "Time",
    labelFontColor: "white"
  },
  axisY: {
    title: "Data per Second",
    titleFontColor: "white",
    labelFontColor: "white",
labelFormatter: function (e) {
  let value = e.value;
  if (value >= 1e12) { // TB
    return (value / 1e12).toFixed(2) + " TB";
  } else if (value >= 1e9) { // GB
    return (value / 1e9).toFixed(2) + " GB";
  } else if (value >= 1e6) { // MB
    return (value / 1e6).toFixed(2) + " MB";
  } else if (value >= 1e3) { // KB
    return (value / 1e3).toFixed(2) + " KB";
  } else {
    return value + " bytes";
  }
}
  },
  axisYType: "secondary",
  data: [
    {
      type: "line",
      name: "Data per Second",
      showInLegend: true,
      legendText: "Data per Second",
      lineColor: "white",
      markerSize: 1,
      dataPoints: dpsData
    }
  ]
});
    let chart = new CanvasJS.Chart("chartContainer", {
      backgroundColor: "black",
      title: {
        text: "Live PPS and DPS",
        fontColor: "white"
      },
      axisX: {
        title: "Time",
        labelFontColor: "white"
      },
      axisY: {
        title: "Packets per Second",
        titleFontColor: "white",
        labelFontColor: "white"
      },
      axisYType: "secondary",
      data: [
        {
          type: "line",
          name: "Packets per Second",
          showInLegend: true,
          legendText: "Packet per Second",
          lineColor: "red",
          markerSize: 1,
          dataPoints: dpsPacket
        }
      ]
    });
    function fetchData() {
      fetch('/server/state')
        .then(response => response.json())
        .then(data => {
		if(data == 'ACK_ok')return;
          // Update the Players Map table
const playersTable = document.querySelector('#players-table');
const playersSize = document.querySelector('#players-size');
playersSize.innerHTML = data.players_map.length; // Update the size

// ... (Update the Players Map table content)

// Update the Clients Map table and size
const clientsTable = document.querySelector('#clients-table');
const clientsSize = document.querySelector('#clients-size');
clientsSize.innerHTML = data.clients_map.length; // Update the size

// ... (Update the Clients Map table content)

// Update the Worlds Map table and size
const worldsTable = document.querySelector('#worlds-table');
const worldsSize = document.querySelector('#worlds-size');
worldsSize.innerHTML = data.worlds_map.length; 

          playersTable.innerHTML = '';
          if (data.players_map.length === 0) {
            playersTable.innerHTML = '<p>No data available</p>';
          } else {
            for (const pp of data.players_map) {
              const row = document.createElement('tr');
              row.innerHTML = '<td>' + pp.name + '</td><td>' + JSON.stringify(pp) + '</td>';
              playersTable.appendChild(row);
            };
          }

          // Update the Clients Map table
          clientsTable.innerHTML = '';
          if (data.clients_map.length === 0) {
            clientsTable.innerHTML = '<p>No data available</p>';
          } else {
            data.clients_map.forEach(client => {
              const row = document.createElement('tr');
              row.innerHTML = '<td>' + client[0] + '</td><td>' + JSON.stringify(client[1]) + '</td>';
              clientsTable.appendChild(row);
            });
          }

          // Update the Worlds Map table
          worldsTable.innerHTML = '';
          if (data.worlds_map.length === 0) {
            worldsTable.innerHTML = '<p>No data available</p>';
          } else {
            for (const world of data.worlds_map) {
              const row = document.createElement('tr');
              row.innerHTML = '<td>' + world.name + '</td><td>' + JSON.stringify(world) + '</td>';
              worldsTable.appendChild(row);
            };
          }

          if (data.pps && data.dps) {
			dpsData.push({x:dpsxVal, y: data.dps});
			dpsxVal++;
            dpsPacket.push({
              x: xVal,
              y: data.pps,
            });
            xVal++;
          }	  
          chart.render();
          dpschart.render();
        })
        .catch(error => console.error('Error fetching data:', error));
    }

    // Fetch data every 1 second
    fetchData();
    setInterval(fetchData, 1000);
  </script>
</body>
</html>`);
res.end();
return;
}else {
res.writeHead(404, { // 404 Not Found
'Content-Type': 'text/html'
});
res.end('Page not found.');
return;
}
}).listen(443);
console.log('okey running.');
let server = dgram.createSocket('udp4');
const zlib = require('zlib');
let ip = '127.0.0.1';
let port = 6003;
ack_shit();
function ack_shit(){
	peer_send('ACK_1', ip, port);
	setInterval(function(){
		peer_send('check_1', ip, port);
		peer_send('status_1', ip, port);
	}, 1000);
};
server.on('message', function(d){
let dx = zlib.inflateSync(d).toString('utf-8');
data = dx
});
function peer_send(str,ip,port){
  let d = zlib.deflateSync(str.toString());
  server.send(d, port, ip, (err) => {});
};

console.log('https://127.0.0.1:443/');
