import { useState } from "react";
import { generateNFTRequest } from "@/lib/api";

export const useGenerateNFT = () => {
  const [assetUrl, setAssetUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const generateNFT = async (prompt: string) => {
    setLoading(true);
    setAssetUrl(null);
    try {
      const response = await generateNFTRequest(prompt);
      setAssetUrl(response.asset_url);
    } catch (error) {
      console.error("Error generating NFT:", error);
    } finally {
      setLoading(false);
    }
  };

  return { generateNFT, assetUrl, loading };
};
