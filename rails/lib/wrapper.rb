require 'arecibolib/arecibo'
require 'pp'
require 'socket'
require 'time'

class ActionController::Base
  def self.send_errors_to_arecibo error_class = Exception
     rescue_from error_class do |exception|
         report_to_arecibo exception
     end
  end
  
  
  def report_to_arecibo exception
    data = {
      :account => ARECIBO_ACCOUNT_NUMBER,
      :msg => "",
      :url => "#{request.protocol}#{request.host_with_port}#{request.request_uri}",
      :user_agent => request.user_agent,
      :server => Socket.gethostname,
      :ip => request.remote_ip,
      :uid => Time.new.to_i
    }
    
    name = exception.class.name
    if name == "ActionController::RoutingError"
        data[:status] = 404
        data[:priority] = 5
    else
        data[:status] = 500
        data[:priority] = 1
    end
    
    data[:type] = exception.class.name
    data[:traceback] = "#{exception.backtrace.join("\n")}"
    # make a nice message out of the post data
    request.env.each { |k, v| data[:msg] += "#{k.to_s}: #{v.to_s}\n"  }
    
    p = Arecibo.new(data)
    p.send
  end
end
