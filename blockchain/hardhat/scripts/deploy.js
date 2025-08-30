async function main() {
const CarbonCredits = await ethers.getContractFactory("CarbonCredits");
const cc = await CarbonCredits.deploy();
await cc.deployed();
console.log("CarbonCredits deployed to:", cc.address);
}


main().catch((error) => {
console.error(error);
process.exitCode = 1;
});