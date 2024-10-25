exports.validateInput = (userAddress, tokenAmount) => {
  if (!userAddress || typeof userAddress !== 'string') {
    throw new Error('Invalid user address');
  }
  if (!tokenAmount || typeof tokenAmount !== 'number' || tokenAmount <= 0) {
    throw new Error('Invalid token amount');
  }
};

