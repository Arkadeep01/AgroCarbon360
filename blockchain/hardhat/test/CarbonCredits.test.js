const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CarbonCredits", function () {
  let CarbonCredits;
  let carbonCredits;
  let owner;
  let verifier;
  let user1;
  let user2;

  beforeEach(async function () {
    // Get signers
    [owner, verifier, user1, user2] = await ethers.getSigners();

    // Deploy contract
    CarbonCredits = await ethers.getContractFactory("CarbonCredits");
    carbonCredits = await CarbonCredits.deploy();
    await carbonCredits.deployed();

    // Add verifier
    await carbonCredits.addVerifier(verifier.address);
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await carbonCredits.owner()).to.equal(owner.address);
    });

    it("Should have correct name and symbol", async function () {
      expect(await carbonCredits.name()).to.equal("AgroCarbon360 Carbon Credits");
      expect(await carbonCredits.symbol()).to.equal("AGROCC");
    });

    it("Should start with zero total supply", async function () {
      expect(await carbonCredits.totalSupply()).to.equal(0);
    });
  });

  describe("Verifier Management", function () {
    it("Should allow owner to add verifier", async function () {
      await expect(carbonCredits.addVerifier(user1.address))
        .to.emit(carbonCredits, "VerifierAdded")
        .withArgs(user1.address);
      
      expect(await carbonCredits.verifiers(user1.address)).to.be.true;
    });

    it("Should allow owner to remove verifier", async function () {
      await carbonCredits.addVerifier(user1.address);
      
      await expect(carbonCredits.removeVerifier(user1.address))
        .to.emit(carbonCredits, "VerifierRemoved")
        .withArgs(user1.address);
      
      expect(await carbonCredits.verifiers(user1.address)).to.be.false;
    });

    it("Should not allow non-owner to add verifier", async function () {
      await expect(
        carbonCredits.connect(user1).addVerifier(user2.address)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });

  describe("Carbon Credit Minting", function () {
    const mintParams = {
      to: user1.address,
      amount: ethers.utils.parseEther("100"),
      projectId: "PROJ001",
      verificationId: "VER001",
      methodology: "IPCC Tier 1",
      location: "India",
      vintageYear: 2023
    };

    it("Should allow verifier to mint credits", async function () {
      await expect(
        carbonCredits.connect(verifier).mintCarbonCredits(
          mintParams.to,
          mintParams.amount,
          mintParams.projectId,
          mintParams.verificationId,
          mintParams.methodology,
          mintParams.location,
          mintParams.vintageYear
        )
      ).to.emit(carbonCredits, "CarbonCreditMinted")
        .withArgs(
          mintParams.to,
          mintParams.amount,
          mintParams.projectId,
          mintParams.verificationId,
          await ethers.provider.getBlock("latest").then(b => b.timestamp)
        );

      expect(await carbonCredits.balanceOf(mintParams.to)).to.equal(mintParams.amount);
      expect(await carbonCredits.totalMinted()).to.equal(mintParams.amount);
    });

    it("Should not allow non-verifier to mint credits", async function () {
      await expect(
        carbonCredits.connect(user1).mintCarbonCredits(
          mintParams.to,
          mintParams.amount,
          mintParams.projectId,
          mintParams.verificationId,
          mintParams.methodology,
          mintParams.location,
          mintParams.vintageYear
        )
      ).to.be.revertedWith("Only verifier or owner");
    });

    it("Should not allow minting to zero address", async function () {
      await expect(
        carbonCredits.connect(verifier).mintCarbonCredits(
          ethers.constants.AddressZero,
          mintParams.amount,
          mintParams.projectId,
          mintParams.verificationId,
          mintParams.methodology,
          mintParams.location,
          mintParams.vintageYear
        )
      ).to.be.revertedWith("Invalid recipient address");
    });

    it("Should not allow minting zero amount", async function () {
      await expect(
        carbonCredits.connect(verifier).mintCarbonCredits(
          mintParams.to,
          0,
          mintParams.projectId,
          mintParams.verificationId,
          mintParams.methodology,
          mintParams.location,
          mintParams.vintageYear
        )
      ).to.be.revertedWith("Amount must be greater than 0");
    });
  });

  describe("Carbon Credit Retirement", function () {
    const mintAmount = ethers.utils.parseEther("100");
    const retireAmount = ethers.utils.parseEther("50");
    const retireReason = "Carbon offset for company emissions";

    beforeEach(async function () {
      // Mint some credits first
      await carbonCredits.connect(verifier).mintCarbonCredits(
        user1.address,
        mintAmount,
        "PROJ001",
        "VER001",
        "IPCC Tier 1",
        "India",
        2023
      );
    });

    it("Should allow user to retire credits", async function () {
      const initialBalance = await carbonCredits.balanceOf(user1.address);
      const initialTotalRetired = await carbonCredits.totalRetired();

      await expect(
        carbonCredits.connect(user1).retireCarbonCredits(retireAmount, retireReason)
      ).to.emit(carbonCredits, "CarbonCreditRetired")
        .withArgs(
          user1.address,
          retireAmount,
          retireReason,
          await ethers.provider.getBlock("latest").then(b => b.timestamp)
        );

      expect(await carbonCredits.balanceOf(user1.address)).to.equal(initialBalance.sub(retireAmount));
      expect(await carbonCredits.totalRetired()).to.equal(initialTotalRetired.add(retireAmount));
    });

    it("Should not allow retiring more than balance", async function () {
      const balance = await carbonCredits.balanceOf(user1.address);
      const tooMuch = balance.add(ethers.utils.parseEther("1"));

      await expect(
        carbonCredits.connect(user1).retireCarbonCredits(tooMuch, retireReason)
      ).to.be.revertedWith("Insufficient balance");
    });

    it("Should not allow retiring with empty reason", async function () {
      await expect(
        carbonCredits.connect(user1).retireCarbonCredits(retireAmount, "")
      ).to.be.revertedWith("Retirement reason cannot be empty");
    });
  });

  describe("Metadata", function () {
    it("Should store and retrieve metadata correctly", async function () {
      const mintParams = {
        to: user1.address,
        amount: ethers.utils.parseEther("100"),
        projectId: "PROJ001",
        verificationId: "VER001",
        methodology: "IPCC Tier 1",
        location: "India",
        vintageYear: 2023
      };

      await carbonCredits.connect(verifier).mintCarbonCredits(
        mintParams.to,
        mintParams.amount,
        mintParams.projectId,
        mintParams.verificationId,
        mintParams.methodology,
        mintParams.location,
        mintParams.vintageYear
      );

      const metadata = await carbonCredits.getCarbonCreditMetadata(0);
      
      expect(metadata.projectId).to.equal(mintParams.projectId);
      expect(metadata.verificationId).to.equal(mintParams.verificationId);
      expect(metadata.methodology).to.equal(mintParams.methodology);
      expect(metadata.location).to.equal(mintParams.location);
      expect(metadata.vintageYear).to.equal(mintParams.vintageYear);
      expect(metadata.isRetired).to.be.false;
    });
  });

  describe("Pausable", function () {
    it("Should allow owner to pause and unpause", async function () {
      await carbonCredits.pause();
      expect(await carbonCredits.paused()).to.be.true;

      await carbonCredits.unpause();
      expect(await carbonCredits.paused()).to.be.false;
    });

    it("Should not allow transfers when paused", async function () {
      // Mint some credits
      await carbonCredits.connect(verifier).mintCarbonCredits(
        user1.address,
        ethers.utils.parseEther("100"),
        "PROJ001",
        "VER001",
        "IPCC Tier 1",
        "India",
        2023
      );

      // Pause contract
      await carbonCredits.pause();

      // Try to transfer
      await expect(
        carbonCredits.connect(user1).transfer(user2.address, ethers.utils.parseEther("10"))
      ).to.be.revertedWith("Pausable: paused");
    });
  });

  describe("ERC20 Functions", function () {
    beforeEach(async function () {
      // Mint some credits
      await carbonCredits.connect(verifier).mintCarbonCredits(
        user1.address,
        ethers.utils.parseEther("100"),
        "PROJ001",
        "VER001",
        "IPCC Tier 1",
        "India",
        2023
      );
    });

    it("Should transfer credits correctly", async function () {
      const transferAmount = ethers.utils.parseEther("50");
      
      await expect(
        carbonCredits.connect(user1).transfer(user2.address, transferAmount)
      ).to.emit(carbonCredits, "Transfer")
        .withArgs(user1.address, user2.address, transferAmount);

      expect(await carbonCredits.balanceOf(user2.address)).to.equal(transferAmount);
    });

    it("Should handle approvals correctly", async function () {
      const approveAmount = ethers.utils.parseEther("30");
      
      await carbonCredits.connect(user1).approve(user2.address, approveAmount);
      expect(await carbonCredits.allowance(user1.address, user2.address)).to.equal(approveAmount);
    });
  });
});
