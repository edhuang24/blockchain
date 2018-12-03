require 'sinatra'
require 'colorize'
require 'active_support/time'
require_relative 'client'
require 'json'

##################

Thread.abort_on_exception = true

def every(seconds)
  Thread.new do
    loop do
      sleep seconds
      yield
    end
  end
end

def render_state
  puts "-" * 40
  STATE.to_a.sort_by(&:first).each do |port, (movie, version_number)|
    puts "#{port.to_s.green} currently likes #{movie.yellow}"
  end
  puts "-" * 40
end

def update_state(update)
  update.each do |port, (movie, version_number)|
    next if port.nil?

    if [movie, version_number].any?(&:nil?)
      STATE[port] ||= nil
    else
      STATE[port] = [STATE[port], [movie, version_number]].compact.max_by(&:last)
    end
  end
end

##################

PORT, PEER_PORT = ARGV.first(2)
set :port, PORT

STATE = ThreadSafe::Hash.new()

update_state(PORT => nil)
update_state(PEER_PORT => nil)

MOVIES = File.readlines("movies.txt").map(&:chomp)
@favorite_movie = MOVIES.sample
@version_number = 0
puts "My favorite movie is #{@favorite_movie.green}"

update_state(PORT => [@favorite_movie, @version_number])

every(8.seconds) do
  puts "I don't like #{@favorite_movie.red} anymore"
  @version_number += 1
  @favorite_movie = MOVIES.sample
  update_state(PORT => [@favorite_movie, @version_number])
  puts "My new favorite movie is #{@favorite_movie}"
end

every(3.seconds) do
  STATE.keys.each do |port|
    next if port == PORT
    puts "Fetching update from #{port.to_s.green}"
    begin
      gossip_response = Client.gossip(port, JSON.dump(STATE))
      update_state(JSON.load(gossip_response))
    rescue Faraday::ConnectionFailed => e
      STATE.delete(port)
    end
  end
  render_state
end

# @param state
post '/gossip' do
  their_state = params[:state]
  update_state(JSON.load(their_state))
  JSON.dump(STATE)
end
