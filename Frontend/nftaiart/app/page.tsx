"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import PromptForm from "@/components/PromptForm";
import { ethers } from "ethers";

type GenerateResponse = {
  image_url: string;
  metadata_url: string;
  transaction_hash: string;
};

export default function Home() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [metadataUrl, setMetadataUrl] = useState<string | null>(null);
  const [transactionHash, setTransactionHash] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mintStatus, setMintStatus] = useState<string | null>(null);
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [networkName, setNetworkName] = useState<string | null>(null);

  useEffect(() => {
    checkIfWalletIsConnected();

    const { ethereum } = window as any;
    if (ethereum) {
      ethereum.on('accountsChanged', handleAccountsChanged);
      ethereum.on('chainChanged', () => window.location.reload());
    }

    return () => {
      if (ethereum && ethereum.removeListener) {
        ethereum.removeListener('accountsChanged', handleAccountsChanged);
        ethereum.removeListener('chainChanged', () => {});
      }
    };
  }, []);

  const handleAccountsChanged = (accounts: string[]) => {
    if (accounts.length > 0) {
      setWalletConnected(true);
      setWalletAddress(accounts[0]);
    } else {
      setWalletConnected(false);
      setWalletAddress(null);
    }
  };

  const checkIfWalletIsConnected = async () => {
    try {
      const { ethereum } = window as any;
      if (!ethereum) return;

      const accounts = await ethereum.request({ method: "eth_accounts" });
      if (accounts.length > 0) {
        setWalletConnected(true);
        setWalletAddress(accounts[0]);

        const provider = new ethers.providers.Web3Provider(ethereum);
        const network = await provider.getNetwork();
        setNetworkName(network.name === 'unknown' ? 'Local Network' : network.name);
      }
    } catch (err) {
      console.error("Error checking wallet connection:", err);
    }
  };

  const connectWallet = async () => {
    try {
      const { ethereum } = window as any;
      if (!ethereum) {
        alert("Please install MetaMask!");
        return;
      }
      setLoading(true);
      const accounts = await ethereum.request({ method: "eth_requestAccounts" });
      if (accounts.length > 0) {
        setWalletConnected(true);
        setWalletAddress(accounts[0]);

        const provider = new ethers.providers.Web3Provider(ethereum);
        const network = await provider.getNetwork();
        setNetworkName(network.name === 'unknown' ? 'Local Network' : network.name);
      }
    } catch (err: any) {
      console.error("Error connecting wallet:", err);
      setError(err.message || "Failed to connect wallet");
    } finally {
      setLoading(false);
    }
  };

  const disconnectWallet = () => {
    setWalletConnected(false);
    setWalletAddress(null);
    setNetworkName(null);
  };

  const handlePromptSubmit = async (prompt: string) => {
    if (!walletConnected || !walletAddress) {
      setError("Please connect your wallet first.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setImageUrl(null);
      setMetadataUrl(null);
      setMintStatus(null);
      setTransactionHash(null);

      setMintStatus("🎨 Generating and minting your NFT...");

      const res = await axios.post<GenerateResponse>("http://localhost:8000/api/generate", {
        prompt,
        wallet_address: walletAddress,
      });

      setImageUrl(res.data.image_url);
      setMetadataUrl(res.data.metadata_url);
      setTransactionHash(res.data.transaction_hash);
      setMintStatus("✅ NFT successfully minted to your wallet!");
    } catch (err: any) {
      console.error("Error during generation:", err);
      setError(err.response?.data?.detail || "Failed to generate and mint NFT. Please try again.");
      setMintStatus("❌ Minting failed");
    } finally {
      setLoading(false);
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#0d0dd7] via-[#16213e] to-[#0f3460] text-white p-6 flex flex-col items-center justify-center">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-7xl font-extrabold tracking-tight text-purple-300 drop-shadow-lg mb-4 font-serif">
          🎨 AI NFT Art Generator
        </h1>
        <p className="text-lg text-gray-300 mb-10">
          Describe your vision, and let AI bring it to life – it will mint it to your wallet automatically.
        </p>

        {!walletConnected ? (
          <button
            onClick={connectWallet}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mb-6 transition-colors"
          >
            {loading ? 'Connecting...' : 'Connect Wallet'}
          </button>
        ) : (
          <div className="mb-6">
            <div className="bg-green-900/30 p-3 rounded-lg inline-block">
              <p className="text-green-400 font-medium">
                {networkName && `${networkName} • `}{walletAddress && formatAddress(walletAddress)} ✓
              </p>
            </div>
            <button
              onClick={disconnectWallet}
              className="text-sm text-gray-400 hover:text-gray-300 mt-2 underline"
            >
              Disconnect
            </button>
          </div>
        )}

        <PromptForm onSubmit={handlePromptSubmit} isWalletConnected={walletConnected} />

        {loading && (
          <div className="mt-6 flex justify-center items-center">
            <svg className="animate-spin h-6 w-6 mr-2 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-yellow-400 font-semibold">{mintStatus || "Processing..."}</p>
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-900/40 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {imageUrl && (
          <div className="mt-10 bg-white/10 backdrop-blur-sm p-4 rounded-xl shadow-xl text-white border border-purple-500/30">
            <img
              src={imageUrl}
              alt="Generated AI Art"
              className="rounded-lg w-full object-cover shadow-2xl"
            />
            <div className="mt-4 space-y-3">
              {mintStatus && (
                <p className={`font-semibold ${mintStatus.includes("✅") ? "text-green-400" : "text-red-400"}`}>
                  {mintStatus}
                </p>
              )}
              <div className="flex flex-col gap-2 text-sm">
                {metadataUrl && (
                  <a
                    href={metadataUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    View Metadata on IPFS →
                  </a>
                )}
                {transactionHash && (
                  <a
                    href={`https://etherscan.io/tx/${transactionHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    View Transaction on Etherscan →
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
