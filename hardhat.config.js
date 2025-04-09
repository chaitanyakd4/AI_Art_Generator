require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.21",
  paths: {
    sources: "./contracts",
    artifacts: "./artifacts",
  },
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
};
