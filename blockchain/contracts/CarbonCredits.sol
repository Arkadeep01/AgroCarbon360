// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title CarbonCredits
 * @dev ERC20 token representing carbon credits with additional metadata
 */
contract CarbonCredits is ERC20, Ownable, Pausable, ReentrancyGuard {
    
    // Carbon credit metadata structure
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
    
    // Mapping from token ID to metadata
    mapping(uint256 => CarbonCreditMetadata) public creditMetadata;
    
    // Total credits minted and retired
    uint256 public totalMinted;
    uint256 public totalRetired;
    
    // Verifier addresses
    mapping(address => bool) public verifiers;
    
    // Events
    event CarbonCreditMinted(
        address indexed to,
        uint256 amount,
        string projectId,
        string verificationId,
        uint256 verificationDate
    );
    
    event CarbonCreditRetired(
        address indexed from,
        uint256 amount,
        string reason,
        uint256 retirementDate
    );
    
    event VerifierAdded(address indexed verifier);
    event VerifierRemoved(address indexed verifier);
    
    // Modifiers
    modifier onlyVerifier() {
        require(verifiers[msg.sender] || msg.sender == owner(), "Only verifier or owner");
        _;
    }
    
    constructor() ERC20("AgroCarbon360 Carbon Credits", "AGROCC") {
        _mint(msg.sender, 0); // Initialize with 0 tokens
    }
    
    /**
     * @dev Mint carbon credits with metadata
     * @param to Recipient address
     * @param amount Amount of credits to mint
     * @param projectId Project identifier
     * @param verificationId Verification identifier
     * @param methodology Methodology used
     * @param location Project location
     * @param vintageYear Vintage year
     */
    function mintCarbonCredits(
        address to,
        uint256 amount,
        string memory projectId,
        string memory verificationId,
        string memory methodology,
        string memory location,
        uint256 vintageYear
    ) external onlyVerifier nonReentrant whenNotPaused {
        require(to != address(0), "Invalid recipient address");
        require(amount > 0, "Amount must be greater than 0");
        require(bytes(projectId).length > 0, "Project ID cannot be empty");
        require(bytes(verificationId).length > 0, "Verification ID cannot be empty");
        
        // Create metadata
        CarbonCreditMetadata memory metadata = CarbonCreditMetadata({
            projectId: projectId,
            verificationId: verificationId,
            verificationDate: block.timestamp,
            methodology: methodology,
            location: location,
            vintageYear: vintageYear,
            isRetired: false,
            retirementReason: "",
            retirementDate: 0
        });
        
        // Store metadata
        creditMetadata[totalMinted] = metadata;
        
        // Mint tokens
        _mint(to, amount);
        totalMinted += amount;
        
        emit CarbonCreditMinted(
            to,
            amount,
            projectId,
            verificationId,
            block.timestamp
        );
    }
    
    /**
     * @dev Retire carbon credits (burn with reason)
     * @param amount Amount to retire
     * @param reason Reason for retirement
     */
    function retireCarbonCredits(
        uint256 amount,
        string memory reason
    ) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        require(bytes(reason).length > 0, "Retirement reason cannot be empty");
        
        // Update metadata for retired credits
        for (uint256 i = 0; i < totalMinted; i++) {
            if (!creditMetadata[i].isRetired) {
                creditMetadata[i].isRetired = true;
                creditMetadata[i].retirementReason = reason;
                creditMetadata[i].retirementDate = block.timestamp;
                break;
            }
        }
        
        // Burn tokens
        _burn(msg.sender, amount);
        totalRetired += amount;
        
        emit CarbonCreditRetired(
            msg.sender,
            amount,
            reason,
            block.timestamp
        );
    }
    
    /**
     * @dev Add a verifier address
     * @param verifier Address to add as verifier
     */
    function addVerifier(address verifier) external onlyOwner {
        require(verifier != address(0), "Invalid verifier address");
        require(!verifiers[verifier], "Already a verifier");
        
        verifiers[verifier] = true;
        emit VerifierAdded(verifier);
    }
    
    /**
     * @dev Remove a verifier address
     * @param verifier Address to remove as verifier
     */
    function removeVerifier(address verifier) external onlyOwner {
        require(verifiers[verifier], "Not a verifier");
        
        verifiers[verifier] = false;
        emit VerifierRemoved(verifier);
    }
    
    /**
     * @dev Pause the contract
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause the contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Get carbon credit metadata
     * @param tokenId Token ID
     * @return metadata Carbon credit metadata
     */
    function getCarbonCreditMetadata(uint256 tokenId) 
        external 
        view 
        returns (CarbonCreditMetadata memory metadata) 
    {
        require(tokenId < totalMinted, "Token ID does not exist");
        return creditMetadata[tokenId];
    }
    
    /**
     * @dev Override transfer function to check if contract is paused
     */
    function transfer(address to, uint256 amount) 
        public 
        virtual 
        override 
        whenNotPaused 
        returns (bool) 
    {
        return super.transfer(to, amount);
    }
    
    /**
     * @dev Override transferFrom function to check if contract is paused
     */
    function transferFrom(address from, address to, uint256 amount) 
        public 
        virtual 
        override 
        whenNotPaused 
        returns (bool) 
    {
        return super.transferFrom(from, to, amount);
    }
}
