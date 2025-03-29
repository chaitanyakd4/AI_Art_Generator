import { useState } from "react";
import { generateNFTRequest } from "@/lib/api"; // Ensure this file exists

export const useGenerateNFT = () => {
  const [assetUrl, setAssetUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateNFT = async (prompt: string) => {
    setLoading(true);
    setAssetUrl(null);
    setError(null);
    
    try {
      const response = await generateNFTRequest(prompt);
      setAssetUrl(response.asset_url);
    } catch (err) {
      console.error("Error generating NFT:", err);
      setError("Failed to generate NFT. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return { generateNFT, assetUrl, loading, error };
};
