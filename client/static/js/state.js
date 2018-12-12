window.state = {};
let colors = {
  1111: 'black',
  2222: 'red',
  3333: 'blue',
  4444: 'green'
};

setInterval(function () {
  $.ajax({
    method: 'GET',
    url: '/api/state'
  }).then(function (data) {
    // debugger
      window.state = data;
      document.getElementById("state").innerHTML = ""
      Object.keys(window.state).forEach(function (port) {
        // debugger
        let state_div = `<p style="color: ${colors[port]}">[PORT ${port}]: ${window.state[port]["parsed_blockchain"].replace("<", "&lt;").replace(">", "&gt;")}</p>`;
        document.getElementById("state").innerHTML += state_div;
      });
  });
}, 1000);
