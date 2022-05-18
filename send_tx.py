from typing import Dict
from typing import List
from typing import Tuple

from web3 import Web3
from web3.contract import Contract
from web3.types import ChecksumAddress
from web3.middleware import geth_poa_middleware

from eth_keyfile import load_keyfile
from eth_keyfile import decode_keyfile_json
from eth_account import Account
from eth_account.signers.local import LocalAccount

# 服务地址
TEST_HTTP_PROVIDER = 'https://testnet-rpc1.coinex.net/'
# MAINNET_HTTP_PROVIDER = 'https://rpc.coinex.net'
HTTP_PROVIDER = TEST_HTTP_PROVIDER

# 签名地址keystore文件
KEYFILE = 'keystore/yofo.keystore'
PASSWORD = 'shit'

# 合约目录
CONTRACT_PATH = './abi'

# 合约名
ERC721_NAME = 'ERC721'
ERC1155_NAME = 'ERC1155'

ERC721_ADDRESS = Web3.toChecksumAddress('0x9106dc5211D7f5F3A4CE0e25bC9A66D35317336D')
ERC1155_ADDRESS = Web3.toChecksumAddress('0x96c7F607601dB45d2A21159d8851057C14910d10')

TX_STATUS_SUCCESS = 1


def get_web3_instance(provider: str):
    provider = Web3.HTTPProvider(provider)
    w3 = Web3(provider)
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def load_keystore(fp: str, password: str) -> LocalAccount:
    """读取keystore文件创建账户"""
    return Account.privateKeyToAccount(decode_keyfile_json(load_keyfile(fp), password.encode('utf-8')))


def read_abi(contract_name: str) -> str:
    with open('{}/{}.abi'.format(CONTRACT_PATH, contract_name), 'r') as fd:
        return fd.read()


def get_erc721_contract(w3: Web3):
    return w3.eth.contract(address=ERC721_ADDRESS, abi=read_abi(ERC721_NAME))


def get_erc1155_contract(w3: Web3):
    return w3.eth.contract(address=ERC1155_ADDRESS, abi=read_abi(ERC1155_NAME))


def signed_and_send_transaction(
        w3: Web3,
        account: LocalAccount,
        c: Contract,
        function: str,
        params: Tuple,
        value: int = None,
        wait: bool = True
) -> Dict:
    nonce = w3.eth.getTransactionCount(account.address, block_identifier='pending')

    t = {
        'from': account.address,
        'nonce': nonce,
        'gasPrice': 500 * (10 ** 9)
    }
    if isinstance(value, int):
        t['value'] = value

    gas = getattr(c.functions, function)(*params).estimateGas(t)

    t['gas'] = int(gas * 1.3)
    transaction = getattr(c.functions, function)(*params).buildTransaction(t)

    signed = account.signTransaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

    success = True
    address = Web3.toChecksumAddress('0x0000000000000000000000000000000000000000')

    if wait:
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=600, poll_latency=1)
        success = tx_receipt.get('status') == TX_STATUS_SUCCESS
        address = tx_receipt['contractAddress']

    return {
        'success': success,
        'address': address,
        'tx_hash': tx_hash.hex()
    }


def print_tx_result(result: Dict):
    print('tx_hash: {}\nsuccess: {}'.format(result['tx_hash'], result['success']))


def erc721_mint(w3: Web3, account: LocalAccount, token_id: int, uri: str, to: ChecksumAddress = None) -> Dict:
    """ERC721增发Token"""
    if not to:
        to = account.address
    params = (to, token_id, uri)

    return signed_and_send_transaction(w3, account, get_erc721_contract(w3), 'mint', params)


def erc1155_mint_batch(
        w3: Web3,
        account: LocalAccount,
        token_ids: List[int],
        amounts: List[int],
        to: ChecksumAddress = None
) -> Dict:
    """ERC1155批量增发Token"""
    if not to:
        to = account.address
    params = (to, token_ids, amounts)

    return signed_and_send_transaction(w3, account, get_erc1155_contract(w3), 'mintBatch', params)


def main():
    w3 = get_web3_instance(HTTP_PROVIDER)
    account = load_keystore(KEYFILE, PASSWORD)

    erc721_metadata_uris = [
        'https://link.ap1.storjshare.io/s/juetcgn2mcf7pcsz5l2fxnqhsrrq/succulents/json/succulent1.json?download=1',
        'https://link.ap1.storjshare.io/s/jwbpjgdomzpc3jg2jtryeic57seq/succulents/json/succulent2.json?download=1',
        'https://link.ap1.storjshare.io/s/jv3jjaofhkwrihaitm3574rf6dfq/succulents/json/succulent3.json?download=1',
        'https://link.ap1.storjshare.io/s/jucqn7pscmojpkisbdwnovg53s7a/succulents/json/succulent4.json?download=1',
        'https://link.ap1.storjshare.io/s/jwyk5os6xg4bi3epnisocqlszeza/succulents/json/succulent5.json?download=1',
        'https://link.ap1.storjshare.io/s/jv3z4fucwqgwaiddqcgx2tfpmyka/succulents/json/succulent6.json?download=1',
        'https://link.ap1.storjshare.io/s/jxpaa2zbydoerwmro64j7mhutkhq/succulents/json/succulent7.json?download=1'
    ]
    for index, uri in enumerate(erc721_metadata_uris):
        print_tx_result(erc721_mint(w3, account, index + 1, uri))

    nft_count = 7
    erc1155_ids = [index for index in range(1, nft_count + 1)]
    erc1155_amounts = [1 for _ in range(nft_count)]
    print_tx_result(erc1155_mint_batch(w3, account, erc1155_ids, erc1155_amounts))


if __name__ == '__main__':
    main()
