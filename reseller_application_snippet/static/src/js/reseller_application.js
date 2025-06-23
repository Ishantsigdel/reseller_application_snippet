
odoo.define('reseller_application.reseller_form', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.ResellerForm = publicWidget.Widget.extend({
        selector: '.s_reseller_application',
        events: {
            'click #become-reseller-btn': '_onBecomeResellerClick',
            'click #submit-application': '_onSubmitApplication',
        },

        _onBecomeResellerClick: function () {
            $('#resellerModal').modal('show');
        },

        _onSubmitApplication: function () {
            var self = this;
            var formData = new FormData(document.getElementById('reseller-form'));

            if (!formData.get('name') || !formData.get('email')) {
                alert('Please fill in all required fields');
                return;
            }

            $.ajax({
                url: '/reseller/apply',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (result) {
                    var response = JSON.parse(result);
                    if (response.success) {
                        alert('Application submitted successfully!');
                        $('#resellerModal').modal('hide');
                        document.getElementById('reseller-form').reset();
                    } else {
                        alert(response.message);
                    }
                },
                error: function () {
                    alert('An error occurred. Please try again.');
                }
            });
        }
    });
});