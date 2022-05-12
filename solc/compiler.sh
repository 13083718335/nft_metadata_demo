rm -rf abi/*
./solc/solc-macosx-amd64-v0.8.0+commit.c7dfd78e --bin --abi contracts/ERC721.sol --overwrite --optimize -o abi/
./solc/solc-macosx-amd64-v0.8.0+commit.c7dfd78e --bin --abi contracts/ERC1155.sol --overwrite --optimize -o abi/
