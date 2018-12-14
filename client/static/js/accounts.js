window.accounts = {};
let colors = {
};

setInterval(function () {
  $.ajax({
    method: 'GET',
    url: '/api/balances'
  }).then(function (data) {
      window.accounts = data;
      debugger
      document.getElementById("accounts").innerHTML = ""
      Object.keys(window.accounts).forEach(function (account) {
      });
      Object.keys(window.accounts).forEach(function (account) {
        // debugger
        // string = window.state[account]["parsed_blockchain"].replace("<", "&lt;").replace(">", "&gt;")
        // split_string = string.split(", ")
        // idx = split_string[0].indexOf("length:")
        // block_length = split_string[0].slice(idx + 8, split_string[0].length)
        // el = `<span style="color: darkorange; font-weight: bold;">${block_length}</span>`
        // new_string = split_string[0].slice(0, idx + 8) + el + ", " + split_string[1]
        // let accounts_div = `<p style="color: ${colors[account]}">[PORT ${account}]: ${new_string}</p>`;
        let accounts_div = `<p style="color: ${colors[account]}">[PORT ${account}]: ${new_string}</p>`;
        document.getElementById("state").innerHTML += state_div;
      });
  });
}, 2000);
