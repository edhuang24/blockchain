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
    url: '/getstate'
  }).then(function (data) {
      window.state = data;
      document.getElementById("state").innerHTML = ""
      Object.keys(window.state).forEach(function (port) {
        let state_div = `<p style="color: ${colors[port]}">port ${port} likes ${window.state[port][0]}<p>`;
        document.getElementById("state").innerHTML += state_div;
      });
  });
}, 1000);
