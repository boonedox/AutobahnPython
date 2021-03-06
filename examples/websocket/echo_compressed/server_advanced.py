###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS

from autobahn.compress import *


class EchoServerProtocol(WebSocketServerProtocol):

   def onConnect(self, connectionRequest):
      pass

   def onOpen(self):
      print "WebSocket extensions in use: %s" % self.websocket_extensions_in_use

   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WebSocketServerFactory("ws://localhost:9000",
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoServerProtocol

#   factory.setProtocolOptions(autoFragmentSize = 4)

   ## Enable WebSocket extension "permessage-deflate". This is all you
   ## need to do (unless you know what you are doing .. see below)!
   ##
   def accept0(offers):
      for offer in offers:
         if isinstance(offer, PerMessageDeflateOffer):
            return PerMessageDeflateOfferAccept(offer)

   ## Enable experimental compression extensions "permessage-snappy"
   ## and "permessage-bzip2"
   ##
   def accept1(offers):
      for offer in offers:
         if isinstance(offer, PerMessageSnappyOffer):
            return PerMessageSnappyOfferAccept(offer)

         elif isinstance(offer, PerMessageBzip2Offer):
            return PerMessageBzip2OfferAccept(offer)

         elif isinstance(offer, PerMessageDeflateOffer):
            return PerMessageDeflateOfferAccept(offer)

   ## permessage-deflate, server requests the client to do no
   ## context takeover
   ##
   def accept2(offers):
      for offer in offers:
         if isinstance(offer, PerMessageDeflateOffer):
            if offer.acceptNoContextTakeover:
               return PerMessageDeflateOfferAccept(offer, requestNoContextTakeover = True)


   ## permessage-deflate, server requests the client to do no
   ## context takeover, and does not context takeover also
   ##
   def accept3(offers):
      for offer in offers:
         if isinstance(offer, PerMessageDeflateOffer):
            if offer.acceptNoContextTakeover:
               return PerMessageDeflateOfferAccept(offer, requestNoContextTakeover = True, noContextTakeover = True)

   ## permessage-deflate, server requests the client to do use
   ## max window bits specified
   ##
   def accept4(offers):
      for offer in offers:
         if isinstance(offer, PerMessageDeflateOffer):
            if offer.acceptMaxWindowBits:
               return PerMessageDeflateOfferAccept(offer, requestMaxWindowBits = 8)


#   factory.setProtocolOptions(perMessageCompressionAccept = accept0)
#   factory.setProtocolOptions(perMessageCompressionAccept = accept1)
#   factory.setProtocolOptions(perMessageCompressionAccept = accept2)
#   factory.setProtocolOptions(perMessageCompressionAccept = accept3)
   factory.setProtocolOptions(perMessageCompressionAccept = accept4)

   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
