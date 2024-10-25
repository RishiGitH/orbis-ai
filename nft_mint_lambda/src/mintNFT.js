const solanaWeb3 = require('@solana/web3.js');
const fs = require('fs');
const path = require('path');

const MINT_PUBLIC_KEY = 'Your Mint Public Key Here';
const KEYPAIR_PATH = path.join(__dirname, '../secrets/keypair.json');

// Load keypair
const loadKeypair = () => {
  const secret = JSON.parse(fs.readFileSync(KEYPAIR_PATH, 'utf8'));
  return solanaWeb3.Keypair.fromSecretKey(Uint8Array.from(secret));
};

exports.mintNFT = async (userAddress, tokenAmount) => {
  try {
    const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl(process.env.NETWORK));
    const payer = loadKeypair();
    const mintPublicKey = new solanaWeb3.PublicKey(MINT_PUBLIC_KEY);
    const userPublicKey = new solanaWeb3.PublicKey(userAddress);

    // Create the transaction
    const transaction = new solanaWeb3.Transaction();

    // Logic to mint tokens to user's wallet
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

