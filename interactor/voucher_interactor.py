from repository.voucher_db_repository import create_voucher_metadata, delete_voucher, create_voucher, \
    get_voucher_metadata, delete_voucher_metadata


def add_voucher_metadata_to_db(voucher_metadata):
    return create_voucher_metadata(voucher_metadata)

def add_voucher_to_db(voucher):
    return create_voucher(voucher)

def delete_voucher_from_db(voucher_id):
    delete_voucher_response = delete_voucher(voucher_id)
    delete_voucher_metadata_response = delete_voucher_metadata(voucher_id)
    return delete_voucher_response and delete_voucher_metadata_response

def retrieve_voucher_metadata_from_voucher_id(voucher_id):
    return get_voucher_metadata(voucher_id)
