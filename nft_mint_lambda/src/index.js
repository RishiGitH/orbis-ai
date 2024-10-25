require('dotenv').config();  // For local dev

const { mintNFT } = require('./mintNFT');
const { validateInput } = require('./utils');

exports.handler = async (event) => {
  try {
    const requestBody = JSON.parse(event.body);
    const { userAddress, tokenAmount } = requestBody;

    // Validate input
    validateInput(userAddress, tokenAmount);

    // Mint NFT
    const result = await mintNFT(userAddress, tokenAmount);

    return {
      statusCode: 200,
      body: JSON.stringify({ success: true, result }),
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ success: false, error: error.message }),
    };
  }
};

