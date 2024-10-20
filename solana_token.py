import json
import os
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from spl.token.instructions import get_associated_token_address, create_associated_token_account, mint_to
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction
from solders.message import Message
from solders.transaction import VersionedTransaction
from dotenv import load_dotenv

load_dotenv()

def mint_tokens(wallet_path, mint_address, amount):
    # Import our keypair from the wallet file
    with open(wallet_path, 'r') as f:
        wallet = json.load(f)
    keypair = Keypair.from_bytes(wallet)

    # Create a Solana devnet connection
    url = "https://api.devnet.solana.com"
    commitment = Confirmed
    client = Client(url, commitment)

    # Mint address
    mint = Pubkey.from_string(mint_address)

    # Token decimals
    token_decimals = 1_000_000_000_0

    try:
        # Create an ATA
        ata = get_associated_token_address(keypair.pubkey(), mint)
        print(f"Your ata is: {ata}")

        # Create ATA if it doesn't exist
        ata_info = client.get_account_info(ata)
        if ata_info.value is None:
            print("Creating ATA...")
            create_ata_ix = create_associated_token_account(
                payer=keypair.pubkey(),
                owner=keypair.pubkey(),
                mint=mint
            )
            # Convert the instruction to a solders Instruction
            create_ata_ix = Instruction(
                program_id=create_ata_ix.program_id,
                accounts=[{"pubkey": meta.pubkey, "is_signer": meta.is_signer, "is_writable": meta.is_writable} for meta in create_ata_ix.keys],
                data=create_ata_ix.data,
            )
            recent_blockhash = client.get_latest_blockhash().value.blockhash
            message = Message.new_with_blockhash(
                [create_ata_ix],
                keypair.pubkey(),
                recent_blockhash
            )
            tx = VersionedTransaction(message, [keypair])
            tx_sig = client.send_transaction(tx)
            client.confirm_transaction(tx_sig.value)
            print("ATA created")

        # Add mint_to instruction to mint tokens
        transaction = Transaction()
        transaction.add(
        create_associated_token_account(
            payer=minter.public_key, owner=receiver_public_key, mint=mint_address
        ))

        transaction.add(
            mint_to(
                mint=mint_address,
                dest=receiver_token_account,
                authority=minter.public_key,
                amount=1000 * (10**9),  # Minting 1000 tokens, assuming 9 decimal places
            )
        )

        # Send transaction to the Solana blockchain
        response = client.send_transaction(transaction, minter)

    except Exception as e:
        print(f"Oops, something went wrong: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Example usage
if __name__ == "__main__":
    wallet_path = os.environ.get("KEYPAIR_PATH")
    mint_address = os.environ.get("MINT_ADDRESS")
    print(mint_address)
    amount = 10  # Amount to mint
    
    result = mint_tokens(wallet_path, mint_address, amount)
    print(result)
