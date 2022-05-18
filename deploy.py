import eth_keyfile

from web3 import Web3
from web3.middleware import geth_poa_middleware

# 合约目录
CONTRACT_PATH = './abi'

# 服务地址
TEST_HTTP_PROVIDER = 'https://testnet-rpc1.coinex.net/'
# MAINNET_HTTP_PROVIDER = 'https://rpc.coinex.net'
HTTP_PROVIDER = TEST_HTTP_PROVIDER

# 签名地址keystore文件
KEYFILE = 'keystore/yofo.keystore'
PASSWORD = 'shit'

# 合约名
ERC721_NAME = 'ERC721'
ERC1155_NAME = 'ERC1155'

# 创建参数
ERC721_PARAM_NAME = 'YoFo'
ERC721_PARAM_SYMBOL = 'YOFO'

ERC1155_PARAM_URI = 'ipfs://QmYBNaRPN8xwAQ8ovyvHXS8KPtc16izMNkZUMwCvX5VdHg/succulents/succulent'

DEFAULT_FEE_LIMIT = 5000000
GAS_PRICE = 500 * (10 ** 9)


def get_web3_instance():
    provider = Web3.HTTPProvider(HTTP_PROVIDER)
    w3 = Web3(provider)
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def load_keyfile(keyfile, password):
    keyfile_json = eth_keyfile.load_keyfile(keyfile)
    return eth_keyfile.decode_keyfile_json(keyfile_json, password.encode('utf-8'))


def deploy(private_key_bytes, w3, contract_name, *args, **kwargs):
    gas = kwargs.get('gas', DEFAULT_FEE_LIMIT)
    gas_price = kwargs.get('gas_price', GAS_PRICE)

    contract_abi_file = '{}/{}.abi'.format(CONTRACT_PATH, contract_name)
    contract_bin_file = '{}/{}.bin'.format(CONTRACT_PATH, contract_name)
    with open(contract_abi_file, 'r') as fd:
        contract_abi = fd.read()

    with open(contract_bin_file, 'r') as fd:
        contract_bin = fd.read()

    account = w3.eth.account.privateKeyToAccount(private_key_bytes)
    contract_obj = w3.eth.contract(abi=contract_abi, bytecode=contract_bin)
    contract_tx = contract_obj.constructor(*args).buildTransaction({
        'from': account.address,
        'gas': gas,
        'gasPrice': gas_price
    })
    contract_tx['nonce'] = w3.eth.getTransactionCount(account.address)
    contract_tx['gas'] = gas
    contract_tx['gasPrice'] = gas_price

    signed = account.signTransaction(contract_tx)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=600)

    return {
        'status': tx_receipt.get('status'),
        'address': Web3.toChecksumAddress(tx_receipt['contractAddress']),
        'tx_hash': tx_hash.hex()
    }


def main():
    private_key_bytes = load_keyfile(KEYFILE, PASSWORD)
    w3 = get_web3_instance()

    print('Deploy ERC721: ')
    aggregator = deploy(
        private_key_bytes,
        w3,
        ERC721_NAME,
        ERC721_PARAM_NAME,
        ERC721_PARAM_SYMBOL,
        gas=DEFAULT_FEE_LIMIT,
        gas_price=GAS_PRICE
    )
    print('erc721 address: {},\ntx hash: {}\nstatus: {}'.format(
        aggregator.get('address'),
        aggregator.get('tx_hash'),
        aggregator.get('status')
    ))

    print('Deploy ERC1155: ')
    aggregator = deploy(
        private_key_bytes,
        w3,
        ERC1155_NAME,
        ERC1155_PARAM_URI,
        gas=DEFAULT_FEE_LIMIT,
        gas_price=GAS_PRICE
    )
    print('erc1155 address: {},\ntx hash: {}\nstatus: {}'.format(
        aggregator.get('address'),
        aggregator.get('tx_hash'),
        aggregator.get('status')
    ))


if __name__ == '__main__':
    main()
