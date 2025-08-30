const { ethers } = require("hardhat");

async function main() {
  console.log("Starting deployment of CarbonCredits contract...");
  
  try {
    // Get the contract factory
    const CarbonCredits = await ethers.getContractFactory("CarbonCredits");
    console.log("Contract factory created successfully");
    
    // Deploy the contract
    console.log("Deploying CarbonCredits contract...");
    const carbonCredits = await CarbonCredits.deploy();
    
    // Wait for deployment to complete
    await carbonCredits.deployed();
    
    console.log("CarbonCredits deployed successfully!");
    console.log("Contract address:", carbonCredits.address);
    console.log("Deployer address:", await carbonCredits.signer.getAddress());
    
    // Verify contract on Etherscan (if not on localhost)
    const network = await ethers.provider.getNetwork();
    if (network.chainId !== 1337 && network.chainId !== 31337) {
      console.log("Waiting for block confirmations...");
      await carbonCredits.deployTransaction.wait(6);
      
      console.log("Verifying contract on Etherscan...");
      try {
        await hre.run("verify:verify", {
          address: carbonCredits.address,
          constructorArguments: [],
        });
        console.log("Contract verified on Etherscan!");
      } catch (error) {
        console.log("Verification failed:", error.message);
      }
    }
    
    // Log deployment information
    console.log("\n=== Deployment Summary ===");
    console.log("Network:", network.name);
    console.log("Chain ID:", network.chainId);
    console.log("Contract Address:", carbonCredits.address);
    console.log("Deployer:", await carbonCredits.signer.getAddress());
    console.log("Gas Used:", carbonCredits.deployTransaction.gasLimit.toString());
    
  } catch (error) {
    console.error("Deployment failed:", error);
    process.exitCode = 1;
  }
}

// Handle errors
main().catch((error) => {
  console.error("Deployment script failed:", error);
  process.exitCode = 1;
});