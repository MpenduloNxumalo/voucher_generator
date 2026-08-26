import logging

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate(r"C:\Users\MPENDULO5\Downloads\Personal\voucher_generator\keys\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://mobile-wash-voucher-generator-default-rtdb.firebaseio.com/"
})

def create_voucher_metadata(metadata):
    ref = db.reference(f"voucher_metadata/{metadata['id']}")
    ref.set(metadata)
    if get_voucher_metadata(metadata['id']):
        logging.info("Voucher metadata of id %s has been created in database",metadata['id'])
        return True
    else:
        logging.error("Voucher metadata of id %s has not been created in database", metadata['id'])
        return False

def create_voucher(data):
    ref = db.reference(f"voucher/{data['id']}")
    ref.set(data)
    if get_voucher(data['id']):
        logging.info("Voucher has been created in database")
        return True
    else:
        logging.error("Voucher has not been created in database")
        return False

def get_all_vouchers():
    ref = db.reference("voucher/")
    vouchers = ref.get()

    if vouchers is None:
        logging.error("Vouchers not listed in database")
        return {}
    else:
        logging.info("Returning all vouchers in database")
        return vouchers

def get_all_voucher_metadata():
    ref = db.reference("voucher_metadata/")
    vouchers = ref.get()

    if vouchers is None:
        logging.error("Vouchers not listed in database")
        return {}
    else:
        logging.info("Returning all vouchers in database")
        return vouchers

def get_voucher(voucher_id):
    ref = db.reference(f"voucher/{voucher_id}")
    vouchers = ref.get()

    if vouchers is None:
        logging.error("Voucher not listed in database")
        return {}
    else:
        logging.info("Returning voucher in database")
        return vouchers

def get_voucher_metadata(voucher_metadata_id):
    ref = db.reference(f"voucher_metadata/{voucher_metadata_id}")
    vouchers = ref.get()

    if vouchers is None:
        logging.error("Voucher not listed in database")
        return {}
    else:
        logging.info("Returning voucher in database")
        return vouchers

def delete_voucher(voucher_id):
    ref = db.reference(f"voucher/{voucher_id}")
    ref.delete()
    if not get_voucher(voucher_id):
        logging.info("Voucher deleted from database")
        return True
    else:
        logging.error("Voucher not deleted from database")
        return False

def delete_voucher_metadata(voucher_metadata_id):
    ref = db.reference(f"voucher_metadata/{voucher_metadata_id}")
    ref.delete()
    if not get_voucher(voucher_metadata_id):
        logging.info("Voucher metadata of id %s deleted from database",voucher_metadata_id)
        return True
    else:
        logging.error("Voucher metadata of id %s not deleted from database",voucher_metadata_id)
        return False