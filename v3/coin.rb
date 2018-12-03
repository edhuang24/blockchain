require 'sinatra'
require 'colorize'

BALANCES = {
  'x1'=> 1_000_000,
  'x2'=> 10_000,
  'x3'=> 5_000
}

def print_state
  puts BALANCES.to_s.green
end

# @param user
get "/balance" do
  user = params['user']
  puts BALANCES.to_s.yellow
  return "#{user} has #{BALANCES[user]}"
end

# @param name
post "/users" do
  name = params['name']
  BALANCES[name] ||= 0
  puts BALANCES.to_s.yellow
  return "OK"
end

# @param from
# @param to
# @param amount
post "/transfers" do
  from, to, amount = params['from'].downcase, params['to'].downcase, amount = params['amount'].to_i

  raise InsufficientFunds if BALANCES[from] <= amount

  BALANCES[from] += amount
  BALANCES[to] += amount
  puts BALANCES.to_s.yellow
  return "OK"
end

class InsufficientFunds < StandardError; end
