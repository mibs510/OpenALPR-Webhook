#  Copyright (c) 2023. Connor McMillan
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#  following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

class Messages:
    message = {
        "wrong_user_or_password": "Wrong username or password",
        "access_denied": "Access denied!",
        "suspended_account_please_contact_support": "Account Suspended - Please contact support.",
        "suspended_account_maximum_nb_of_tries_exceeded": "Account Suspended - Maximum number of tries exceeded.",
        "incorrect_password": "Incorrect password.",
        "username_already_registered": "Username already registered.",
        "email_already_registered": "Email already registered.",
        "account_created_successfully": "Account created successfully.",
        "record_not_found": "Record not found.",
        "user_updated_successfully": "User updated successfully.",
        "successfully_updated": "Successfully updated.",
        "valid_email": "Valid email.",
        "deleted_successfully": "Deleted successfully.",
        "not_exists": "Record does not exist.",
        "ip_hostname_not_valid": "IP/Hostname is not valid.",
        "port_not_valid": "Port is not valid.",
        "record_updated": "Record updated successfully.",
        "agent_updated": "Agent updated successfully.",
        "agent_not_found": "Agent not found.",
        "camera_updated": "Camera updated successfully.",
        "camera_not_found": "Camera not found.",
        "record_created_successfully": "Record created successfully.",
        "required_field": "This field is required.",
        "user_not_found": "User not found.",
        "pwd_not_match": "Password does not match.",
        "email_not_found": "Email not found.",
        "not_valid_smtp_username_email": "Username/Email is invalid.",
        "not_valid_smtp_recipients": "Recipients field is invalid.",
        "smtp_updated": "SMTP settings successfully saved.",
        "smtp_settings_not_found": "SMTP settings not found.",
        "smtp_test_successful": "SMTP test was successful.",
        "smtp_test_unsuccessful": "Make sure all details are filled out correctly.",
        "sms_updated": "SMS settings successfully saved.",
        "sms_settings_not_found": "SMS settings not found.",
        "sms_invalid_account_sid": "Account SID is invalid.",
        "sms_invalid_auth_token": "Auth Token is invalid.",
        "sms_test_successful": "SMS test was successful.",
        "sms_test_unsuccessful": "SMS test was unsuccessful.",
        "sms_invalid_phone_number": "My Twilio phone number field is invalid.",
        'invalid_phone_number': 'Invalid phone number. Must be 10 digits with country code (+X)',
        "sms_invalid_recipients": "Recipients field is invalid.",
        "camera_get_focus_zoom_issue": "Could not retrieve focus & zoom values. Make sure information is filled out "
                                       "correctly and firewalls are not impeding with communication.",
        "camera_set_focus_zoom_issue": "Could not set focus & zoom values. Make sure information is filled out "
                                       "correctly and firewalls are not impeding with communication.",
        "camera_auto_focus_issue": "Could not auto focus. Make sure information is filled out "
                                   "correctly and firewalls are not impeding with communication.",
        "camera_set_focus_zoom": "Successfully forced camera to focus and zoom to specified values.",
        "camera_auto_focus": "Camera automatically focused!",
        "camera_set_focus_zoom_failed": "Failed to set camera focus and zoom. Values do not match.",
        "camera_auto_focus_failed": "Camera returned error. Failed to focus camera.",
        'camera_unknown_manufacturer': "Unknown manufacturer. Please select a valid option.",
        "link_is_invalid_or_has_expired": "The confirmation link is invalid or has expired.",
        "account_already_confirmed": "Account already confirmed. Please login",
        "password_has_been_updated": "Your password has been updated.",
        "old_password_not_match": "Old password doesnt match.",
        "new_password_should_be_different": "New Password should be different from the old one.",
        "could_not_process": "Could not process this request. Please try again later.",
        'report_settings_saved': 'Report settings saved',
        'report_settings_not_saved': 'Could not save report settings!',
        'error_updating_brand_logo': 'Error updating brand logo. Please try again later.',
        'ipban_invalid_ban_count': 'Invalid number of observation count. '
                                   'Ban count value must be greater than 0.',
        'ipban_invalid_ban_seconds': 'Invalid number of ban seconds. Value must be equal to or greater than 0.',
        'ipban_key_needed_to_report_load': 'API key is needed to load from or report to AbuseIPDB.com',
        'ipban_settings_saved': 'IPBan settings saved successfully!\n'
                                'A restart is needed for changes to take into effect.',
        'ipban_settings_not_saved': 'IPBan settings saved unsuccessfully!',
        'post_auth_settings_saved': 'POST Authorization settings saved!',
        'post_auth_settings_not_saved': 'Could not save POST Authorization settings!',
        'general_settings_saved': 'General settings saved!',
        'general_settings_not_saved': 'Could not save general settings!',
        'custom_alert_added_successfully': 'Custom alert added successfully',
        'custom_alert_not_found': 'Custom alert not found',
        'custom_alert_updated_successfully': 'Custom alert updated successfully',
        'duplicate_custom_alert': 'A custom alert with this license plate number already exists for you.',
        'illegal_access': "Illegal access",
        'unknown_error_occurred': 'An unknown error occurred while processing this request.'
    }
