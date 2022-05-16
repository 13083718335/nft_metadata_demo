import os
import json
import requests

from typing import List
from typing import Dict

from urllib.parse import urljoin

pinata_host = 'https://api.pinata.cloud'
pinata_pin_file_to_ipfs_url = urljoin(pinata_host, '/pinning/pinFileToIPFS')

api_key = '1f067a4a99e2595c1449'
api_secret = '0ab1729f4beb801040026cf02c0de4ef718c710f28bf8afaea282b52a3e47c6d'

nft_count = 7

json_filepaths = ['./ipfs/succulents/json/succulent{}.json'.format(index) for index in range(1, nft_count + 1)]

image_filepaths = ['./ipfs/succulents/image/succulent{}.png'.format(index) for index in range(1, nft_count + 1)]

path_name = 'succulents'


def upload_files(filepaths: List[str], pinata_metadata: Dict) -> Dict:
    headers = {
        'pinata_api_key': api_key,
        'pinata_secret_api_key': api_secret
    }

    files = [
        ('file', (path_name + '/' + os.path.basename(filepath), open(filepath, 'rb'))) for filepath in filepaths
    ]

    data = {
        'pinataMetadata': json.dumps(pinata_metadata),
        'pinataOptions': json.dumps({'wrapWithDirectory': True})
    }

    return requests.post(pinata_pin_file_to_ipfs_url, data=data, files=files, headers=headers).json()


def upload_images() -> Dict:
    pinata_image_metadata = {
        'name': 'SucculentNFT',
        'keyvalues': {
            'author': 'YoFo',
            'type': 'image'
        }
    }

    return upload_files(image_filepaths, pinata_image_metadata)


def upload_jsons() -> Dict:
    pinata_json_metadata = {
        'name': 'SucculentNFT',
        'keyvalues': {
            'author': 'YoFo',
            'type': 'json'
        }
    }

    return upload_files(json_filepaths, pinata_json_metadata)


def main():
    # {
    # 'IpfsHash': 'QmP8YCZNUGaGZtwFYTnD88Ur1Sp98ZbTR1JFan5x5sKfNE',
    # 'PinSize': 8661288,
    # 'Timestamp': '2022-05-13T07:41:06.024Z'
    # }
    # print(upload_images())

    # {
    # 'IpfsHash': 'QmYBNaRPN8xwAQ8ovyvHXS8KPtc16izMNkZUMwCvX5VdHg',
    # 'PinSize': 5395,
    # 'Timestamp': '2022-05-13T08:02:44.589Z'
    # }
    print(upload_jsons())


if __name__ == '__main__':
    main()
