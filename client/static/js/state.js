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
        string = window.state[port]["parsed_blockchain"].replace("<", "&lt;").replace(">", "&gt;")
        split_string = string.split(", ")
        idx = split_string[0].indexOf("length:")
        block_length = split_string[0].slice(idx + 8, split_string[0].length)
        console.log(block_length)
        el = `<span style="color: darkorange; font-weight: bold;">${block_length}</span>`
        new_string = split_string[0].slice(0, idx + 8) + el + ", " + split_string[1]
        let state_div = `<p style="color: ${colors[port]}">[PORT ${port}]: ${new_string}</p>`;
        document.getElementById("state").innerHTML += state_div;
      });
  });
}, 1000);
