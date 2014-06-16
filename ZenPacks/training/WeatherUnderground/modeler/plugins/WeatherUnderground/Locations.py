"""Models locations using the Weather Underground API."""

# stdlib Imports
import json

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin


class Locations(PythonPlugin):

    """Weather Underground locations modeler plugin."""

    relname = 'wundergroundLocations'
    modname = 'ZenPacks.training.WeatherUnderground.WundergroundLocation'

    requiredProperties = (
        'zWundergroundAPIKey',
        'zWundergroundLocations',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Asynchronously collect data from device. Return a deferred."""
        log.info("%s: collecting data", device.id)

        apikey = getattr(device, 'zWundergroundAPIKey', None)
        if not apikey:
            log.error(
                "%s: %s not set. Get one from http://www.wunderground.com/weather/api",
                device.id,
                'zWundergroundAPIKey')

            returnValue(None)

        locations = getattr(device, 'zWundergroundLocations', None)
        if not locations:
            log.error(
                "%s: %s not set.",
                device.id,
                'zWundergroundLocations')

            returnValue(None)

        rm = self.relMap()

        for location in locations:
            try:
                response = yield getPage(
                    'http://autocomplete.wunderground.com/aq?query={query}'
                    .format(query=location))

                response = json.loads(response)
            except Exception, e:
                log.error(
                    "%s: %s", device.id, e)

                returnValue(None)

            for result in response['RESULTS']:
                rm.append(self.objectMap({
                    'id': self.prepId(result['l']),
                    'title': result['name'],
                    'api_link': result['l'],
                    'country_code': result['c'],
                    'timezone': result['tzs'],
                    }))

        returnValue(rm)

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""
        if results is None:
            return None

        log.info("%s: processing data", device.id)
        return results
