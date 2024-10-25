const solanaWeb3 = require('@solana/web3.js');

exports.mintNFT = async (userAddress, tokenAmount) => {
  try {
    const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl(process.env.NETWORK));
    const payer = loadKeypairFromEnv();
    const mintPublicKey = new solanaWeb3.PublicKey(process.env.MINT_PUBLIC_KEY);
    const userPublicKey = new solanaWeb3.PublicKey(userAddress);

    // Create the transaction
    const transaction = new solanaWeb3.Transaction();

    // Minting logic
    for (let i = 0; i < tokenAmount; i++) {
      const tokenAccount = await solanaWeb3.getOrCreateAssociatedTokenAccount(
        connection,
        payer,
        mintPublicKey,
        userPublicKey
      );

      const mintInstruction = solanaWeb3.Token.createMintToInstruction(
        solanaWeb3.TOKEN_PROGRAM_ID,
        mintPublicKey,
        tokenAccount.address,
        payer.publicKey,
        [],
        1 // Mint 1 token per iteration
      );

      transaction.add(mintInstruction);
    }

    // Send the transaction
    const signature = await solanaWeb3.sendAndConfirmTransaction(connection, transaction, [payer]);
    return { signature, userAddress, tokenAmount };
  } catch (error) {
    console.error('Error during minting:', error);
    throw new Error('Failed to mint NFT.');
  }
};

const loadKeypairFromEnv = () => {
  const secretKey = JSON.parse(process.env.WALLET_SECRET); // Load from environment
  return solanaWeb3.Keypair.fromSecretKey(Uint8Array.from(secretKey));
};

