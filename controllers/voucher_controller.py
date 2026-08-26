import logging

from interactor.voucher_interactor import retrieve_voucher_metadata_from_voucher_id
from models.voucher_exceptions import BadRequest, InternalServerError, InvalidSignature
from util.voucher_util import generate_private_and_public_keys, generate_vouchers, verify_signature, \
    validate_request_body, validate_voucher_type_and_voucher_amount, configure_logger

keys_directory = r"C:\Users\MPENDULO5\Downloads\Personal\voucher_generator\keys"
storage_directory = r"C:\Users\MPENDULO5\Downloads\Personal\voucher_generator\voucher_qr_codes"

private_key, public_key = generate_private_and_public_keys(keys_directory)


def generate_n_amount_of_vouchers(body):
    try:
        voucher_type = body["voucher_type"]
        amount_of_vouchers = body["amount_of_vouchers"]
        validate_voucher_type_and_voucher_amount(voucher_type, amount_of_vouchers)
        configure_logger()
        return generate_vouchers(private_key, amount_of_vouchers, voucher_type, storage_directory), 201
    except BadRequest as e:
        return False, e.status_code
    except InternalServerError as e:
        return False, e.status_code


def verify_voucher_validity(body):
    try:
        validate_request_body(body)
        signature = bytes.fromhex(body["signature"])
        logging.info("Signature has been extracted")

        message = retrieve_voucher_metadata_from_voucher_id(body["id"])
        del message["signature"]
        del message["image"]

        return verify_signature(message, signature, public_key)
    except BadRequest as e:
        return False, e.status_code
    except InvalidSignature as e:
        return False, e.status_code
    except InternalServerError as e:
        return False, e.status_code
