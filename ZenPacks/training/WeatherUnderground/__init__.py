from . import zenpacklib


CFG = zenpacklib.ZenPackSpec(
    name=__name__,

    zProperties={
        'DEFAULTS': {'category': 'Weather Underground'},

        'zWundergroundAPIKey': {
            'type': 'string',
            'default': '',
        },

        'zWundergroundLocations': {
            'type': 'lines',
            'default': ['Austin, TX', 'San Jose, CA', 'Annapolis, MD'],
        },
    },

    classes={
        'WundergroundDevice': {
            'base': zenpacklib.Device,
            'label': 'Weather Underground API',
        },

        'WundergroundLocation': {
            'base': zenpacklib.Component,
            'label': 'Location',
            'properties': {
                'country_code': {
                    'label': 'Country Code',
                    'order': 4.0,
                },

                'timezone': {
                    'label': 'Time Zone',
                    'order': 4.1,
                },

                'weather': {
                    'label': 'Weather',
                    'order': 4.2,
                },

                'api_link': {
                    'label': 'API Link',
                    'order': 4.9,
                    'grid_display': False,
                },
            }
        },
    },

    class_relationships=zenpacklib.relationships_from_yuml(
        """[WundergroundDevice]++-[WundergroundLocation]"""
        )
)

CFG.create()
