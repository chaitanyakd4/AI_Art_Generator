export const generateNFTRequest = async (prompt: string) => {
    const response = await fetch("http://127.0.0.1:8000/generate-nft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt_text: prompt }),
    });
  
    if (!response.ok) throw new Error("Failed to generate NFT");
  
    return response.json();
  };
  