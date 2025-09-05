"""
Blockchain integration client for AgroCarbon360
Handles interactions with the CarbonCredits smart contract
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3.exceptions import ContractLogicError, ValidationError
from eth_account import Account
from eth_account.messages import encode_defunct

logger = logging.getLogger(__name__)

class CarbonCreditsClient:
    """Client for interacting with the CarbonCredits smart contract"""
    
    def __init__(self, rpc_url: str = None, contract_address: str = None, private_key: str = None):
        """
        Initialize the blockchain client
        
        Args:
            rpc_url: Ethereum RPC URL
            contract_address: CarbonCredits contract address
            private_key: Private key for transactions (optional)
        """
        self.rpc_url = rpc_url or os.getenv("ETHEREUM_RPC_URL", "http://localhost:8545")
        self.contract_address = contract_address or os.getenv("CARBON_CREDITS_CONTRACT_ADDRESS")
        self.private_key = private_key or os.getenv("ETHEREUM_PRIVATE_KEY")
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Ethereum network at {self.rpc_url}")
        
        # Load contract ABI
        self.contract_abi = self._load_contract_abi()
        
        # Initialize contract
        if self.contract_address:
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
        
        # Set up account if private key is provided
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.w3.eth.default_account = self.account.address
        else:
            self.account = None
    
    def _load_contract_abi(self) -> List[Dict]:
        """Load the contract ABI from the compiled artifacts"""
        try:
            # Try to load from hardhat artifacts
            abi_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../blockchain/hardhat/artifacts/contracts/CarbonCredits.sol/CarbonCredits.json"
            )
            
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    artifact = json.load(f)
                    return artifact['abi']
            else:
                # Fallback to a basic ABI for common functions
                logger.warning("Contract ABI not found, using basic ABI")
                return self._get_basic_abi()
                
        except Exception as e:
            logger.error(f"Failed to load contract ABI: {e}")
            return self._get_basic_abi()
    
    def _get_basic_abi(self) -> List[Dict]:
        """Get a basic ABI for common ERC20 and CarbonCredits functions"""
        return [
            # ERC20 functions
            {"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
            {"inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
            
            # CarbonCredits specific functions
            {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "projectId", "type": "string"}, {"name": "verificationId", "type": "string"}, {"name": "methodology", "type": "string"}, {"name": "location", "type": "string"}, {"name": "vintageYear", "type": "uint256"}], "name": "mintCarbonCredits", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
            {"inputs": [{"name": "amount", "type": "uint256"}, {"name": "reason", "type": "string"}], "name": "retireCarbonCredits", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
            {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "getCarbonCreditMetadata", "outputs": [{"components": [{"name": "projectId", "type": "string"}, {"name": "verificationId", "type": "string"}, {"name": "verificationDate", "type": "uint256"}, {"name": "methodology", "type": "string"}, {"name": "location", "type": "string"}, {"name": "vintageYear", "type": "uint256"}, {"name": "isRetired", "type": "bool"}, {"name": "retirementReason", "type": "string"}, {"name": "retirementDate", "type": "uint256"}], "name": "metadata", "type": "tuple"}], "stateMutability": "view", "type": "function"},
            
            # Events
            {"anonymous": False, "inputs": [{"indexed": True, "name": "to", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}, {"indexed": False, "name": "projectId", "type": "string"}, {"indexed": False, "name": "verificationId", "type": "string"}, {"indexed": False, "name": "verificationDate", "type": "uint256"}], "name": "CarbonCreditMinted", "type": "event"},
            {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"}, {"indexed": False, "name": "amount", "type": "uint256"}, {"indexed": False, "name": "reason", "type": "string"}, {"indexed": False, "name": "retirementDate", "type": "uint256"}], "name": "CarbonCreditRetired", "type": "event"}
        ]
    
    def get_balance(self, address: str) -> int:
        """Get carbon credits balance for an address"""
        try:
            balance = self.contract.functions.balanceOf(address).call()
            return balance
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return 0
    
    def mint_carbon_credits(
        self,
        to_address: str,
        amount: int,
        project_id: str,
        verification_id: str,
        methodology: str,
        location: str,
        vintage_year: int
    ) -> Optional[str]:
        """
        Mint carbon credits with metadata
        
        Args:
            to_address: Recipient address
            amount: Amount of credits to mint
            project_id: Project identifier
            verification_id: Verification identifier
            methodology: Methodology used
            location: Project location
            vintage_year: Vintage year
            
        Returns:
            Transaction hash if successful, None otherwise
        """
        if not self.account:
            raise ValueError("Private key required for minting")
        
        try:
            # Build transaction
            transaction = self.contract.functions.mintCarbonCredits(
                to_address,
                amount,
                project_id,
                verification_id,
                methodology,
                location,
                vintage_year
            ).build_transaction({
                'from': self.account.address,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Successfully minted {amount} carbon credits to {to_address}")
                return receipt.transactionHash.hex()
            else:
                logger.error("Transaction failed")
                return None
                
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to mint carbon credits: {e}")
            return None
    
    def retire_carbon_credits(self, amount: int, reason: str) -> Optional[str]:
        """
        Retire carbon credits
        
        Args:
            amount: Amount to retire
            reason: Reason for retirement
            
        Returns:
            Transaction hash if successful, None otherwise
        """
        if not self.account:
            raise ValueError("Private key required for retiring credits")
        
        try:
            # Build transaction
            transaction = self.contract.functions.retireCarbonCredits(
                amount,
                reason
            ).build_transaction({
                'from': self.account.address,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Successfully retired {amount} carbon credits")
                return receipt.transactionHash.hex()
            else:
                logger.error("Transaction failed")
                return None
                
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to retire carbon credits: {e}")
            return None
    
    def get_carbon_credit_metadata(self, token_id: int) -> Optional[Dict]:
        """Get metadata for a specific carbon credit token"""
        try:
            metadata = self.contract.functions.getCarbonCreditMetadata(token_id).call()
            return {
                'projectId': metadata[0],
                'verificationId': metadata[1],
                'verificationDate': metadata[2],
                'methodology': metadata[3],
                'location': metadata[4],
                'vintageYear': metadata[5],
                'isRetired': metadata[6],
                'retirementReason': metadata[7],
                'retirementDate': metadata[8]
            }
        except Exception as e:
            logger.error(f"Failed to get metadata for token {token_id}: {e}")
            return None
    
    def get_total_supply(self) -> int:
        """Get total supply of carbon credits"""
        try:
            return self.contract.functions.totalSupply().call()
        except Exception as e:
            logger.error(f"Failed to get total supply: {e}")
            return 0
    
    def get_total_minted(self) -> int:
        """Get total minted carbon credits"""
        try:
            return self.contract.functions.totalMinted().call()
        except Exception as e:
            logger.error(f"Failed to get total minted: {e}")
            return 0
    
    def get_total_retired(self) -> int:
        """Get total retired carbon credits"""
        try:
            return self.contract.functions.totalRetired().call()
        except Exception as e:
            logger.error(f"Failed to get total retired: {e}")
            return 0
    
    def is_verifier(self, address: str) -> bool:
        """Check if an address is a verifier"""
        try:
            return self.contract.functions.verifiers(address).call()
        except Exception as e:
            logger.error(f"Failed to check verifier status for {address}: {e}")
            return False
    
    def get_network_info(self) -> Dict:
        """Get network information"""
        try:
            return {
                'chain_id': self.w3.eth.chain_id,
                'block_number': self.w3.eth.block_number,
                'gas_price': self.w3.eth.gas_price,
                'is_connected': self.w3.is_connected()
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {}