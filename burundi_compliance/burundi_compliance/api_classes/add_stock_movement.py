import requests
from ..doctype.custom_exceptions import AuthenticationError, StockMovementError
import frappe
from .base import OBRAPIBase
from ..utils.base_api import full_api_url
class TrackStockMovement:

    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 2

    def __init__(self, token, max_retries=5, retry_delay_seconds=2):
        obr_base = OBRAPIBase()
        self.BASE_TRACK_STOCK_MOVEMENT_API_URL = full_api_url(obr_base.get_api_from_ebims_settings("add_stock_movement"))
        self.token = token
        self.MAX_RETRIES = max_retries
        self.RETRY_DELAY_SECONDS = retry_delay_seconds

    def _retry_request(self, data, retries):
        try:
            response = requests.post(self.BASE_TRACK_STOCK_MOVEMENT_API_URL, json=data, headers=self._get_headers())
            response.raise_for_status()
            
            # Validate the response structure
            if not response.json().get("success"):
                frappe.log_error(f"Unexpected API response format: {response.text}")
                raise StockMovementError(f"Unexpected API response format: {response.text}")

            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"Error during API request: {str(e)}"
            frappe.log_error(error_message, "Add Stock Movement Request Error")
            frappe.log_error(f"Response content: {response.text}")
            
            # # Resend the items to OBR
            # if retries > 0:
            #     frappe.logger().warning(f"Retrying in {self.RETRY_DELAY_SECONDS} seconds... ({self.MAX_RETRIES - retries + 1}/{self.MAX_RETRIES})")
            #     time.sleep(self.RETRY_DELAY_SECONDS)
            #     return self._retry_request(data, retries - 1)
            # else:
            #     raise AuthenticationError(f"Max retries reached. {error_message}")

    def _send_request(self, data):
        return self._retry_request(data, self.MAX_RETRIES)
        

    def _handle_response(self, response):
        # frappe.throw(str(response))
        if response.get("success"):
            # Handle successful stock movement response, if needed
            return response.get('msg')
        else:
            raise StockMovementError(response["msg"])

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def post_stock_movement(self, stock_movement_data):
        response = self._send_request(stock_movement_data)
        return self._handle_response(response)

    
        
			