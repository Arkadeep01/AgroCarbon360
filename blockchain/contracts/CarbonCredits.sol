// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;


contract CarbonCredits {
address public owner;
uint256 public totalSupply;


mapping(address => uint256) private balances;
mapping(address => mapping(address => uint256)) private allowances;


event Mint(address indexed to, uint256 amount, string metadata);
event Transfer(address indexed from, address indexed to, uint256 amount);
event Burn(address indexed from, uint256 amount);


modifier onlyOwner() {
require(msg.sender == owner, "only owner");
_;
}


constructor() {
owner = msg.sender;
}


function mint(address to, uint256 amount, string calldata metadata) external onlyOwner returns (bool) {
require(to != address(0), "zero address");
balances[to] += amount;
totalSupply += amount;
emit Mint(to, amount, metadata);
return true;
}


function balanceOf(address account) external view returns (uint256) {
return balances[account];
}


function transfer(address to, uint256 amount) external returns (bool) {
address from = msg.sender;
require(balances[from] >= amount, "insufficient");
balances[from] -= amount;
balances[to] += amount;
emit Transfer(from, to, amount);
return true;
}


// simple burn function
function burn(uint256 amount) external returns (bool) {
address from = msg.sender;
require(balances[from] >= amount, "insufficient");
balances[from] -= amount;
totalSupply -= amount;
emit Burn(from, amount);
return true;
}
}