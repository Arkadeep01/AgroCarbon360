# AgroCarbon360 Blockchain

Smart contracts and blockchain integration for the AgroCarbon360 carbon credits platform.

## Overview

This project contains:
- **CarbonCredits.sol**: ERC20-compliant smart contract for carbon credits with metadata
- **Hardhat configuration**: Development and deployment setup
- **Backend integration**: Python client for blockchain interactions

## Features

- **ERC20 Compliance**: Standard token functionality (transfer, approve, etc.)
- **Carbon Credit Metadata**: Stores project information, verification details, and retirement data
- **Verifier System**: Role-based access control for credit minting
- **Retirement Tracking**: Permanent retirement of credits with reasons
- **Pausable**: Emergency pause functionality
- **Security**: Reentrancy protection and access controls

## Smart Contract Functions

### Core Functions
- `mintCarbonCredits()`: Mint new carbon credits with metadata
- `retireCarbonCredits()`: Permanently retire credits
- `getCarbonCreditMetadata()`: Retrieve credit metadata
- `addVerifier()` / `removeVerifier()`: Manage verifier addresses

### ERC20 Functions
- `transfer()`: Transfer credits between addresses
- `approve()` / `transferFrom()`: Allowance-based transfers
- `balanceOf()`: Check account balance

## Setup

### Prerequisites

- Node.js 16+
- npm or yarn
- Python 3.11+ (for backend integration)

### Installation

1. Install dependencies:
```bash
npm install
cd hardhat && npm install
```

2. Set up environment variables:
```bash
# Copy example environment file
cp .env.example .env
# Edit .env with your configuration
```

3. Compile contracts:
```bash
npm run compile
```

## Development

### Local Development

1. Start local Hardhat node:
```bash
npm run node
```

2. Deploy contracts locally:
```bash
npm run deploy:local
```

3. Run tests:
```bash
npm run test
```

### Testnet Deployment

1. Configure testnet in `.env`:
```
TESTNET_RPC_URL=https://sepolia.infura.io/v3/YOUR-PROJECT-ID
PRIVATE_KEY=your-private-key
```

2. Deploy to testnet:
```bash
npm run deploy:testnet
```

### Mainnet Deployment

1. Configure mainnet in `.env`:
```
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR-PROJECT-ID
PRIVATE_KEY=your-private-key
ETHERSCAN_API_KEY=your-etherscan-api-key
```

2. Deploy to mainnet:
```bash
npm run deploy:mainnet
```

## Backend Integration

The backend includes a Python client for blockchain interactions:

```python
from src.blockchain.ledger_client import CarbonCreditsClient

# Initialize client
client = CarbonCreditsClient(
    rpc_url="http://localhost:8545",
    contract_address="0x...",
    private_key="your-private-key"
)

# Mint carbon credits
tx_hash = client.mint_carbon_credits(
    to_address="0x...",
    amount=100000000000000000000,  # 100 tokens (18 decimals)
    project_id="PROJ001",
    verification_id="VER001",
    methodology="IPCC Tier 1",
    location="India",
    vintage_year=2023
)

# Get balance
balance = client.get_balance("0x...")

# Retire credits
tx_hash = client.retire_carbon_credits(
    amount=50000000000000000000,  # 50 tokens
    reason="Carbon offset for company emissions"
)
```

## Contract Architecture

### CarbonCredits Contract

```solidity
contract CarbonCredits is ERC20, Ownable, Pausable, ReentrancyGuard {
    struct CarbonCreditMetadata {
        string projectId;
        string verificationId;
        uint256 verificationDate;
        string methodology;
        string location;
        uint256 vintageYear;
        bool isRetired;
        string retirementReason;
        uint256 retirementDate;
    }
    
    mapping(uint256 => CarbonCreditMetadata) public creditMetadata;
    mapping(address => bool) public verifiers;
    
    uint256 public totalMinted;
    uint256 public totalRetired;
}
```

### Key Features

1. **Metadata Storage**: Each minted credit batch stores project information
2. **Verifier System**: Only authorized verifiers can mint credits
3. **Retirement Tracking**: Credits can be permanently retired with reasons
4. **ERC20 Compliance**: Standard token functionality
5. **Security**: Pausable, reentrancy protection, access controls

## Testing

Run comprehensive tests:

```bash
npm run test
```

Tests cover:
- Contract deployment
- Verifier management
- Credit minting and retirement
- Metadata storage and retrieval
- ERC20 functionality
- Security features

## Gas Optimization

The contract includes:
- Optimizer enabled (200 runs)
- Efficient data structures
- Minimal storage operations
- Batch operations where possible

## Security Considerations

- **Access Control**: Only verifiers can mint credits
- **Reentrancy Protection**: Prevents reentrancy attacks
- **Pausable**: Emergency stop functionality
- **Input Validation**: Comprehensive parameter checks
- **Event Logging**: All important actions are logged

## Deployment Addresses

### Testnet (Sepolia)
- Contract: `0x...` (deploy to get address)

### Mainnet
- Contract: `0x...` (deploy to get address)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
