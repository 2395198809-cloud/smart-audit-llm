# Real-cropped benchmark provenance

## Source files

- `openzeppelin_erc20_v4_9_6.sol`: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC20/ERC20.sol
- `openzeppelin_erc721_v4_9_6.sol`: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC721/ERC721.sol
- `openzeppelin_erc1155_v4_9_6.sol`: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC1155/ERC1155.sol
- `openzeppelin_erc4626_v4_9_6.sol`: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC20/extensions/ERC4626.sol
- `openzeppelin_accesscontrol_v4_9_6.sol`: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/access/AccessControl.sol
- `uniswap_v2_erc20.sol`: https://raw.githubusercontent.com/Uniswap/v2-core/master/contracts/UniswapV2ERC20.sol
- `solmate_erc20.sol`: https://raw.githubusercontent.com/transmissions11/solmate/main/src/tokens/ERC20.sol
- `solmate_erc721.sol`: https://raw.githubusercontent.com/transmissions11/solmate/main/src/tokens/ERC721.sol

## Added vulnerable samples

- `OZERC20MissingAllowanceTransferFrom.sol`
- `OZERC20WrongAllowanceOwnerRealCrop.sol`
- `OZERC20AllowanceNotDecreasedRealCrop.sol`
- `OZERC20PublicBurnFromRealCrop.sol`
- `OZERC20PermitNoSignatureRealCrop.sol`
- `UniswapV2MissingAllowanceTransferFrom.sol`
- `UniswapV2WrongAllowanceOwner.sol`
- `UniswapV2AllowanceNotDecreased.sol`
- `SolmateERC20MissingAllowanceTransferFrom.sol`
- `SolmateERC20PublicBurnFrom.sol`
- `OZERC721MissingApprovalTransferFrom.sol`
- `OZERC721WrongOperatorDirection.sol`
- `OZERC721PublicBurnFrom.sol`
- `SolmateERC721MissingApprovalTransferFrom.sol`
- `SolmateERC721WrongOperatorDirection.sol`
- `OZERC1155MissingOperatorSafeTransfer.sol`
- `OZERC1155WrongOperatorDirection.sol`
- `OZERC1155BatchMissingOperatorRealCrop.sol`
- `OZERC4626WithdrawMissingOwnerAuth.sol`
- `OZERC4626WithdrawWrongOwnerAuth.sol`
- `OZERC4626WithdrawAllowanceNotDecreased.sol`
- `AccessControlRoleBypassTransferRealCrop.sol`
- `AccessControlWrongRoleTransferRealCrop.sol`
- `CompoundStyleTransferFromWrongSpender.sol`
- `AaveVaultWithdrawFromMissingAuth.sol`

## Added safe samples

- `OZERC20SafeTransferFromRealCrop.sol`
- `UniswapV2SafeTransferFromRealCrop.sol`
- `SolmateERC20SafeTransferFromRealCrop.sol`
- `OZERC20SafeBurnFromAllowanceRealCrop.sol`
- `OZERC20SafePermitTransferRealCrop.sol`
- `OZERC721SafeTransferFromRealCrop.sol`
- `OZERC721SafeOperatorTransferRealCrop.sol`
- `SolmateERC721SafeTransferRealCrop.sol`
- `OZERC1155SafeTransferRealCrop.sol`
- `OZERC1155SafeBatchTransferRealCrop.sol`
- `OZERC1155SafeOperatorRealCrop.sol`
- `OZERC4626SafeWithdrawFromRealCrop.sol`
- `OZERC4626SafeRedeemFromRealCrop.sol`
- `AccessControlSafeRoleTransferRealCrop.sol`
- `VaultSafeDelegatedWithdrawRealCrop.sol`
