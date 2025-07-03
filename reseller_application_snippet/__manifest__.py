{
    'name': 'Reseller Application System',
    'version': '16.0.1.0.0',
    'category': 'Website',
    'summary': 'Dynamic website snippet for reseller applications with portal access',
    'author': 'sigdel',
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
            'reseller_application_snippet/static/src/css/reseller_kanban.css',

        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/reseller_backend_views.xml',
        'views/email_template.xml',
        'views/portal_templates.xml',
        'views/reseller_backend_views.xml',
        'views/website_snippet_data.xml',
        'views/website_snippet_templates.xml',
        'views/website_assets.xml',

    ],
    'installable': True,
    'application': True,
}
