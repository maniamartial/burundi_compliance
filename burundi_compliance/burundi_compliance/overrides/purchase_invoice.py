from ..api_classes.base import OBRAPIBase

import frappe
from frappe import _
from ..data.purchase_invoice_data import get_purchase_data_for_stock_update
from ..utils.background_jobs import enqueue_stock_movement
obr_integration_base = OBRAPIBase()
auth_details=obr_integration_base.get_auth_details()

def get_items(doc, movement_type="EN"):
    token = obr_integration_base.authenticate()
    if doc.is_return==1:
        movement_type="SAU"
    items_data = get_purchase_data_for_stock_update(doc, movement_type=movement_type)
    if items_data:
        for item in items_data:
                try:
                    enqueue_stock_movement(item, doc)
                    frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully", alert=True)
                except Exception as e:
                    frappe.msgprint(f"Error sending item {item}: {str(e)}")

def on_submit_update_stock(doc, method=None):
    if doc.update_stock==1:
        try:
            get_items(doc)
        except Exception as e:
            frappe.msgprint(f"Error during submission: {str(e)}")
            
def on_cancel_update_stock(doc, method=None):
    if doc.update_stock==1:
        try:
            get_items(doc, movement_type="SAU")
        except Exception as e:
            frappe.msgprint(f"Error during cancellation: {str(e)}")
