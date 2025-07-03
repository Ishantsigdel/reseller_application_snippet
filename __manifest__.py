{
    'name': 'Reseller Application System',
    'version': '16.0.1.0.0',
    'category': 'Website',
    'summary': 'Dynamic website snippet for reseller applications with portal access',
    'author': 'Ishant-sigdel',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',
        'web',
        'mail'
    ],
    'assets': {
        'web.assets_frontend': [
            'reseller_application_snippet/static/src/js/reseller_application.js',
            'reseller_application_snippet/static/src/css/reseller_style.css',

        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/reseller_views.xml',
        'views/email_template.xml',
        'views/portal_templates.xml',
        'views/website_snippet_data.xml',
        'views/website_snippet_templates.xml',
        'views/website_assets.xml',

    ],
    'installable': True,
    'application': True,
}
