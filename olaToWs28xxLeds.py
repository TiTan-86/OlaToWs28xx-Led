from ola.ClientWrapper import ClientWrapper
import os
import configparser
import time
import datetime
import logging
from rpi_ws281x import Color, PixelStrip, ws
import sys
import traceback

#Original Client!
#def NewData(data):
#  print(data)


#wrapper = ClientWrapper()
#client = wrapper.Client()
#client.RegisterUniverse(universe, client.REGISTER, NewData)
#wrapper.Run()

config = configparser.ConfigParser()
config.read('olaToWs28xxLeds.cfg')
logtime = datetime.datetime.now().strftime("%Y%m%d")
logfile = 'olaWs28xxSender'  + logtime + '.log'
logging.basicConfig(filename=logfile, format='%(asctime)s ; %(name)s ; %(levelname)s ;  %(message)s',
                    level=config.get('LOG', 'logLevel'))


class olaToWS28xxLeds():
  classname = 'olaToWS28xxLeds'
  config = None
  logging = None
  showTerminalDmxSignals = True

  ledUniversum=[1]
  ledStartUniversum = 1 # universum mit dem alles satartee
  ledCount = 1 # Number of LED pixels.
  ledPin = 18 # GPIO pin connected to the pixels (must support PWM!).
  ledFreq = 800000 # LED signal frequency in hertz (usually 800khz)
  ledChannel = 0 # DMA channel to use for generating signal (try 10)
  ledDMA = 10
  ledBrigttness = 255 # full  # Set to 0 for darkest and 255 for brightest
  ledInvert = False # True to invert the signal (when using NPN transistor level shift)
  ledChannelPerLed=3 # Wieviele DMX channel kann ein LED belegen!
  ledArray=None

  ledStartIndex = 0


  objLed = None
  objOlaWrapper = None
  objOlaClient =None

  def log_Error(self, msg=''):
    self.logging.error(self.classname + ' -> ' + msg)

  def log_info(self, msg='', level=1):
    self.logging.info(self.classname + ' -> ' + msg)

  def log_warning(self, msg='', level=1):
    self.logging.warning(self.classname + ' -> ' + msg)

  def log_debug(self, msg='', level=1):
    self.logging.debug(self.classname + ' -> ' + msg)


  def __init__(self , config , logging):
    self.logging = logging
    self.setConfig(config)
    #self.initLed()


  def setConfig(self, config):
    self.log_info('Lade config ')
    self.config = config
    self.ledCount = self.config.getint('LED', 'Count')
    self.ledStartUniversum = self.config.getint('ARTNET', 'startUniversum')
    self.ledPin = self.config.getint('LED', 'pin')
    self.ledFreq = self.config.getint('LED', 'Freq_hz')
    self.ledChannel = self.config.getint('LED', 'Channel')
    self.ledChannelPerLed = self.config.getint('LED', 'ChannelPerLed')
    #herausfinden wieviele universum gebraucht werden!
    if (self.ledCount * self.ledChannel) <= 512:
      self.log_info('es wird nur ein universum gebraucht')
      self.ledUniversum[0] = self.ledStartUniversum
    else:
      #wenn mehr als eins gebau
      restled = self.ledCount - 512
      self.ledUniversum[0] = self.ledStartUniversum

      u = 1
      while restled <= 0:
        self.log_info('es wurde universum '+ u + ' gefunden')
        self.ledUniversum[u] = u
        restled = restled - 512




  ## led Channel Aufbau

  #  - LEDindex
  #  -  - Universum
  #  -  -  -  (DMX Channels in array zugehoerig zu led)
  def createLedArray(self):



    #############################################
    ####    diese funktion gehört noch gebaut!
    #############################################


    #ledIndex = self.ledStartIndex
    #for universum in self.ledUniversum:
    # # while ledindex


  # startet den Universum Client
  def startArtnetClient(self):
    self.log_info('Starte mit Universum Laden')
    for universum in self.ledUniversum:
      self.loadArtNetClient(universum)

  # ladet das Spezielle Universum
  def loadArtNetClient(self,universum):
    self.log_info('Universum ' + str(universum) + ' wird geladen' )
    objOlaWrapper = ClientWrapper()
    objOlaClient = objOlaWrapper.Client()
    objOlaClient.RegisterUniverse(universum, objOlaClient.REGISTER, self.setLeds)
    objOlaWrapper.Run()



  def setLeds (self,data):
    if self.showTerminalDmxSignals == True:
    	os.system('clear')
    	print(data)



  def initLed(self):
    self.log_info('erzeuge led Objekt')
    self.objLed = PixelStrip(self.ledCount, self.ledPin, self.ledFreq, self.ledDMA, self.ledInvert, self.ledBrigttness, self.ledChannel, ws.WS2812_STRIP )
    try:
      self.log_info('starte Led Treiber')
      self.objLed.begin()
    except:
      self.log_Error('haben den treiber nicht stareten koennen')

  ## fertoge Testes
  def wheel(self, pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
      return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
      pos -= 85
      return Color(255 - pos * 3, 0, pos * 3)
    else:
      pos -= 170
      return Color(0, pos * 3, 255 - pos * 3)

  # fertige Tests
  def rainbow(self, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
      for i in range(self.objLed.numPixels()):
        self.objLed.setPixelColor(i, self.wheel((i + j) & 255))
      self.objLed.show()
      time.sleep(wait_ms / 1000.0)



if __name__ == '__main__' :
  #aufbau laden der classe
  olaclient = olaToWS28xxLeds(config ,logging)
  olaclient.startArtnetClient()
