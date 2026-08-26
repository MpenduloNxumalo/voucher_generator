import base64
import datetime
import json
import logging
import os
import shutil
from datetime import timedelta

import cv2
import qrcode
from colorama import init
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption, load_pem_private_key,
    load_pem_public_key
)
from pyzbar.pyzbar import decode

from interactor.voucher_interactor import add_voucher_metadata_to_db, add_voucher_to_db, delete_voucher_from_db
from models import voucher_exceptions
from models.voucher_exceptions import BadRequest


def generate_private_and_public_keys(path):
    os.chdir(path)
    if len(os.listdir(path)) == 0:
        # Generate private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        # Get public key
        public_key = private_key.public_key()
        logging.info("Generated private key")
        logging.info("Generated public key")
        with open("private_key.pem", "wb") as f:
            f.write(
                private_key.private_bytes(
                    Encoding.PEM,
                    PrivateFormat.PKCS8,
                    NoEncryption()
                )
            )
            logging.info("Stored private key")

        with open("public_key.pem", "wb") as f:
            f.write(
                public_key.public_bytes(
                    Encoding.PEM,
                    PublicFormat.SubjectPublicKeyInfo
                )
            )
            logging.info("Stored public key")
    else:

        with open("private_key.pem", "rb") as f:
            private_key = load_pem_private_key(f.read(), password=None)
            logging.info("Loaded private key")

        with open("public_key.pem", "rb") as f:
            public_key = load_pem_public_key(f.read())
            logging.info("Loaded public key")
    return private_key, public_key


def generate_signature(message, private_key):
    payload = json.dumps(message, sort_keys=True, separators=(',', ':')).encode("utf-8")
    return private_key.sign(
        payload,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )


def validate_request_body(data):
    isVoucherIdAndVoucherSignatureEmpty = data["id"] == "" and data["signature"] == ""
    isVoucherIdAndVoucherSignatureNone = data["id"] is not None and data["signature"] is not None

    if isVoucherIdAndVoucherSignatureEmpty and isVoucherIdAndVoucherSignatureNone:
        raise BadRequest("Invalid voucher type or amount of vouchers")
    else:
        return True


def configure_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def validate_voucher_type_and_voucher_amount(voucher_type, amount_of_vouchers):
    isVoucherTypeValid = voucher_type != "" and voucher_type is not None
    isVoucherAmountValid = voucher_type is not None and isinstance(amount_of_vouchers, int) and amount_of_vouchers > 0

    if not (isVoucherTypeValid and isVoucherAmountValid):
        raise BadRequest("Invalid voucher type")


def verify_signature(message, signature, public_key):
    payload = json.dumps(message, sort_keys=True, separators=(',', ':')).encode("utf-8")
    try:
        public_key.verify(
            signature,
            payload,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        logging.info("Signature is valid!")
        delete_voucher_from_db(message['id'])
        return True, 200

    except InvalidSignature:
        logging.error("Signature is invalid!")
        raise voucher_exceptions.InvalidSignature(signature=signature)


def generate_voucher_qr_code(data, vouchers_id, storage_directory):
    qr_code_image_name = f"{vouchers_id}-{len(os.listdir(os.getcwd())) + 1}.png"
    storage_path = f"{storage_directory}\\{qr_code_image_name}"

    os.chdir(storage_directory)
    qr = qrcode.make(data)
    qr.save(qr_code_image_name)
    logging.info(f"QR code generated successfully and can be located at: {storage_path}")
    return storage_path


def generate_signed_voucher(private_key, vouchers_id, voucher_type, storage_directory):
    os.chdir(storage_directory)
    logging.info(f"Current working directory: {os.getcwd()}")
    voucher_metadata = {
        "id": f"{vouchers_id}-{len(os.listdir(os.getcwd())) + 1}",
        "voucher_type": voucher_type,
        "issued": f"{datetime.date.today().strftime('%d/%m/%Y')}",
        "expiry": f"{(datetime.date.today() + timedelta(days=90)).strftime('%d/%m/%Y')}",
    }

    signature = generate_signature(voucher_metadata, private_key)
    voucher_metadata["signature"] = f"{signature.hex()}"
    return voucher_metadata


def generate_base_64_string_from_qr_code(qr_code_image_path):
    with open(qr_code_image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
        logging.info(f"Generated base 64 string from QR code image")
    return base64_string


def generate_voucher_from_voucher_metadata(voucher_metadata):
    return {
        "id": voucher_metadata['id'],
        "signature": voucher_metadata['signature'],
    }


def delete_qr_code_from_vouchers_qr_codes(qr_code_image_directory):
    for item in os.listdir(qr_code_image_directory):
        item_path = os.path.join(qr_code_image_directory, item)

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logging.info(f"Removing directory {item_path}")
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")


def generate_vouchers(private_key, number_of_vouchers, voucher_type, storage_directory):
    init()
    vouchers_list = []
    vouchers_id = ''.join(word[0] for word in voucher_type.split("_"))
    for i in range(number_of_vouchers):
        voucher_metadata = generate_signed_voucher(private_key, vouchers_id, voucher_type, storage_directory)
        voucher = generate_voucher_from_voucher_metadata(voucher_metadata)
        qr_code_image_path = generate_voucher_qr_code(
            json.dumps(voucher, sort_keys=True, separators=(',', ':')).encode("utf-8"), vouchers_id, storage_directory)
        voucher_metadata["image"] = generate_base_64_string_from_qr_code(qr_code_image_path)
        vouchers_list.append(voucher)
        add_voucher_metadata_to_db(voucher_metadata)
        add_voucher_to_db(voucher)
    delete_qr_code_from_vouchers_qr_codes(storage_directory)

    return vouchers_list


def simulate_qr_scan(path):
    img = cv2.imread(path)
    results = decode(img)
    if not results:
        return {}
    data = results[0].data.decode("utf-8")
    return json.loads(data)
