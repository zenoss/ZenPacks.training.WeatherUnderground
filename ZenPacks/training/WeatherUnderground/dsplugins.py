"""Monitors current conditions using the Weather Underground API."""

# Logging
import logging
LOG = logging.getLogger('zen.WeatherUnderground')

# stdlib Imports
import json
import time

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# PythonCollector Imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
    PythonDataSourcePlugin,
    )


class WundergroundPlugin(PythonDataSourcePlugin):

    """Abstract base class for Weather Underground API plugins."""

    TAG = 'override-me'

    @classmethod
    def config_key(cls, datasource, context):
        return (
            context.device().id,
            datasource.getCycleTime(context),
            context.id,
            'wunderground-{tag}'.format(cls.TAG),
            )

    @classmethod
    def params(cls, datasource, context):
        return {
            'api_key': context.zWundergroundAPIKey,
            'api_link': context.api_link,
            'location_name': context.title,
            }

    @inlineCallbacks
    def collect(self, config):
        data = self.new_data()

        for datasource in config.datasources:
            try:
                response = yield getPage(
                    'http://api.wunderground.com/api/{api_key}/{tag}{api_link}.json'
                    .format(
                        api_key=datasource.params['api_key'],
                        api_link=datasource.params['api_link'],
                        tag=self.TAG,
                        ))

                response = json.loads(response)
            except Exception:
                LOG.exception(
                    "%s: failed to get %s data for %s",
                    config.id,
                    self.TAG,
                    datasource.location_name)

                continue

            self.process_response(config, datasource, response, data)

        returnValue(data)

    def process_response(self, config, datasource, response, data):
        """Use config, datasource and response to add to data.

        Should be overridden in concrete subclasses.
        """
        pass


class Conditions(WundergroundPlugin):

    """Weather Underground conditions data source plugin."""

    TAG = 'conditions'

    def process_response(self, config, datasource, response, data):
        current_observation = response['current_observation']
        for datapoint_id in (x.id for x in datasource.points):
            if datapoint_id not in current_observation:
                continue

            try:
                value = current_observation[datapoint_id]
                if isinstance(value, basestring):
                    value = value.strip(' %')

                value = float(value)
            except (TypeError, ValueError):
                # Sometimes values are NA or not available.
                continue

            dpname = '_'.join((datasource.datasource, datapoint_id))
            data['values'][datasource.component][dpname] = (value, 'N')


class Alerts(WundergroundPlugin):

    """Weather Underground alerts data source plugin."""

    TAG = 'alerts'

    def process_response(self, config, datasource, response, data):
        for alert in response['alerts']:
            severity = None

            if int(alert['expires_epoch']) <= time.time():
                severity = 0
            elif alert['significance'] in ('W', 'A'):
                severity = 3
            else:
                severity = 2

            data['events'].append({
                'device': config.id,
                'component': datasource.component,
                'severity': severity,
                'eventKey': 'wu-alert-{}'.format(alert['type']),
                'eventClassKey': 'wu-alert',

                'summary': alert['description'],
                'message': alert['message'],

                'wu-description': alert['description'],
                'wu-date': alert['date'],
                'wu-expires': alert['expires'],
                'wu-phenomena': alert['phenomena'],
                'wu-significance': alert['significance'],
                'wu-type': alert['type'],
                })
