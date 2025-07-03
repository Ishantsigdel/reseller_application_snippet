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
                this._showNotification('error', 'Missing Required Fields', 'Please fill in all required fields');
                return;
            }

            var email = formData.get('email');
            if (email && !email.includes('@')) {
                this._showNotification('error', 'Invalid Email', 'Email must contain "@" symbol');
                return;
            }

            var phone = formData.get('phone');
            if (phone && !/\d/.test(phone)) {
                this._showNotification('error', 'Invalid Phone', 'Phone number must contain at least one digit');
                return;
            }

            var submitBtn = document.getElementById('submit-application');
            var originalText = submitBtn.textContent;
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;

            $.ajax({
                url: '/reseller/apply',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (result) {
                    var response = JSON.parse(result);
                    if (response.success) {
                        self._showNotification('success', 'Success!', 'Application submitted successfully!');
                        $('#resellerModal').modal('hide');
                        document.getElementById('reseller-form').reset();
                        
                        // Optional: Show additional success message after modal closes
                        setTimeout(function() {
                            self._showBannerNotification('success', 'Thank you for your application! We will review it and get back to you soon.');
                        }, 500);
                    } else {
                        self._showNotification('error', 'Submission Failed', response.message || 'Please check your information and try again.');
                    }
                },
                error: function (xhr, status, error) {
                    console.error('AJAX Error:', error);
                    self._showNotification('error', 'Connection Error', 'An error occurred. Please check your connection and try again.');
                },
                complete: function() {
                    // Reset button state
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }
            });
        },

       
        _showNotification: function(type, title, message) {
            // Remove any existing notifications
            $('.custom-notification').remove();
            
            var iconClass = {
                'success': 'fa-check-circle',
                'error': 'fa-exclamation-circle',
                'warning': 'fa-exclamation-triangle',
                'info': 'fa-info-circle'
            };

            var colorClass = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            };

            var notification = $(`
                <div class="alert ${colorClass[type]} alert-dismissible custom-notification" 
                     style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                    <div class="d-flex align-items-center">
                        <i class="fa ${iconClass[type]} mr-2" style="font-size: 18px;"></i>
                        <div>
                            <strong>${title}</strong><br>
                            <small>${message}</small>
                        </div>
                    </div>
                </div>
            `);

            $('body').append(notification);

            // Auto-hide after 5 seconds for success, 7 seconds for others
            var hideDelay = type === 'success' ? 5000 : 5000;
            setTimeout(function() {
                notification.fadeOut();
            }, hideDelay);
        },

     
        _showBannerNotification: function(type, message) {
            $('.banner-notification').remove();
            
            var colorClass = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            };

            var banner = $(`
                <div class="alert ${colorClass[type]} alert-dismissible banner-notification text-center" 
                     style="position: fixed; top: 0; left: 0; right: 0; z-index: 9998; margin: 0; border-radius: 0;">
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                    <strong>${message}</strong>
                </div>
            `);

            $('body').prepend(banner);

            // Auto-hide after 8 seconds
            setTimeout(function() {
                banner.slideUp();
            }, 8000);
        },

    
        _validateForm: function(formData) {
            var errors = [];
            
            // Required fields
            if (!formData.get('name')) {
                errors.push('Full name is required');
            }
            
            if (!formData.get('email')) {
                errors.push('Email is required');
            }
            
            // Email format
            var email = formData.get('email');
            if (email) {
                if (!email.includes('@')) {
                    errors.push('Email must contain "@" symbol');
                }
                
                var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    errors.push('Please enter a valid email address');
                }
            }
            
            // Phone validation
            var phone = formData.get('phone');
            if (phone && !/\d/.test(phone)) {
                errors.push('Phone number must contain at least one digit');
            }
            
            return {
                isValid: errors.length === 0,
                errors: errors
            };
        }
    });

    return publicWidget.registry.ResellerForm;
});