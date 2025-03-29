interface NFTCardProps {
    imageUrl: string;
  }
  
  const NFTCard = ({ imageUrl }: NFTCardProps) => (
    <div className="mt-4 border p-4 rounded-lg shadow-md">
      <img src={imageUrl} alt="Generated NFT" className="w-full h-auto rounded-lg" />
      <p className="mt-2 text-center">Generated NFT</p>
    </div>
  );
  
  export default NFTCard;
  