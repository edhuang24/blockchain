require_relative 'coin'
require 'faraday'

URL = 'http://localhost'
PORT = 4567

def create_user(name)
  Faraday.post("#{URL}:#{PORT}/users", name: name).body
end

def get_balance(user)
  Faraday.get("#{URL}:#{PORT}/balance", user: user).body
end

def transfer(from, to, amount)
  Faraday.get("#{URL}:#{PORT}/transfers", from: from, to: to, amount: amount).body
end
