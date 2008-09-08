# AreciboConnector

require 'net/http'
require 'uri'

class ActionController::Base
  def self.send_errors_to_arecibo error_class = Exception
    rescue_from error_class do |exception|
      report_to_arecibo exception
    end
  end
  
  def report_to_arecibo exception
    puts "Exception Class = #{exception.class.name}"
    puts "Exception Backtrace = #{exception.backtrace.join("\n")}"
    
    Net::HTTP.post_form URI.parse(arecibo_url), form_info_for(exception)
    
    redirect_to '/404.html'
  end
  
  def form_info_for exception
    ARECIBO_INFORMATION.merge :status => 400, :traceback => exception.backtrace.join("\n"), :msg => exception.to_s
  end
  
  def arecibo_url
    'http://arecibo.clearwind.ca/v/1/'
  end
  
end