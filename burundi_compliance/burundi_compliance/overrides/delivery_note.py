from ..api_classes.base import OBRAPIBase
import frappe

from frappe import _
from ..data.delivery_note import get_delivery_note_items, get_delivery_note_items_on_cancel
from ..utils.background_jobs import enqueue_stock_movement
obr_integration_base = OBRAPIBase()
auth_details=obr_integration_base.get_auth_details()

def get_items(doc):
    token = obr_integration_base.authenticate()
    items_data = get_delivery_note_items(doc)
    
    for item in items_data:
            try:

                enqueue_stock_movement(item, doc)
                frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully", alert=True)
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
        
def get_items_on_cancel(doc):
    token = obr_integration_base.authenticate()
    items_data = get_delivery_note_items_on_cancel(doc)
    
    for item in items_data:
            try:
                enqueue_stock_movement(item, doc)
                frappe.msgprint(f"The transaction for {item.get('item_code')} queued successfully")
            except Exception as e:
                frappe.msgprint(f"Error sending item {item}: {str(e)}")
    
def on_submit_or_cancel_update_stock(doc, method=None):
    try:
        get_items(doc)
    except Exception as e:
        frappe.msgprint(f"Error during submission: {str(e)}")
        
def before_cancel_update_stock(doc, method=None):
    try:
        get_items_on_cancel(doc)
    except Exception as e:
        frappe.msgprint(f"Error during submission: {str(e)}")
        