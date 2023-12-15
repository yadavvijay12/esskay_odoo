# -*- coding: utf-8 -*-
{
    'name': "PPTS: Restrict Scheduler Cron on Weekdays and public holidays",
    'summary': """
        This Module restricts the scheduled cron activities on weekoffs and public holidays based on configurations in settings and Public holidays at Timeofff module.
          """,
    'description': """This technical module which sends a survey link to customer via E-mail, WhatsApp based on given configurations and customizations done in Survey, Survey Participants.etc""",
    'category': 'Survey',
    'version': '16.0',
    'installable': True,
    'license': 'OEEL-1',
    'depends': ['base', 'hr_holidays'],
    'data': [
        'views/ir_cron_views.xml',
        'views/res_config_settings_view.xml',
    ],
}
