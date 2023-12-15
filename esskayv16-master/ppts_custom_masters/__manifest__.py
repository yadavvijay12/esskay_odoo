{
    'name': "PPTS : Service Ticket Masters",
    'version': '16.0',
    'summary': """
        This module provides the below masters.
        1. Customer Master
        2. Product Master
        3. Asset Master
        4. Process Master
        5. Region Master
        6.  Roles/Channel
        7.  Asset Category
        8.  Base Type
        9. Industry 
        10. Location
        11. Spare's Package
        12. Vendor List
        13. User Master
        14. Work Location Master
        15. Product Category Master
        16. Contracts
        17. Service Request
        """,
    'author': "PPTS India Pvt Ltd",
    'website': "https://www.pptssolutions.com",
    'category': 'masters',
    'depends': ['base', 'product', 'sale', 'sale_renting', 'ppts_service_request', 'base_geolocalize'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/master_menu_access.xml',
        'views/res_partner_view.xml',
        'views/product_template_view.xml',
        'views/stock_lot_view.xml',
        'views/service_request_view.xml',
        'views/stock_production_lot_view.xml',
        'views/warranty_term_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
