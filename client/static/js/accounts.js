window.accounts = {};
let account_colors = {};
let index_colors = {
  1: 'black',
  2: 'red',
  3: 'blue',
  4: 'green',
  5: 'purple',
  6: 'orange',
  7: 'turquoise'
};

setInterval(function () {
  $.ajax({
    method: 'GET',
    url: '/api/balances'
  }).then(function (data) {
      window.accounts = data;
      // debugger
      document.getElementById("accounts").innerHTML = "";

      Object.keys(window.accounts).forEach(function (account_key, idx) {
        account_colors[account_key] = index_colors[idx]
      });

      Object.keys(window.accounts).forEach(function (account_key) {
        // debugger
        // string = window.state[account]["parsed_blockchain"].replace("<", "&lt;").replace(">", "&gt;")
        // split_string = string.split(", ")
        // idx = split_string[0].indexOf("length:")
        // block_length = split_string[0].slice(idx + 8, split_string[0].length)
        // el = `<span style="color: darkorange; font-weight: bold;">${block_length}</span>`
        // new_string = split_string[0].slice(0, idx + 8) + el + ", " + split_string[1]
        // let accounts_div = `<p style="color: ${colors[account]}">[PORT ${account}]: ${new_string}</p>`;
        let accounts_div = `<p class="account-line" style="color: ${account_colors[account_key]}; font-size: 12px;">[${account_key}]: <strong>${window.accounts[account_key]} BTC</strong></p>`;
        document.getElementById("accounts").innerHTML += accounts_div;
      });
  });
}, 1000);
