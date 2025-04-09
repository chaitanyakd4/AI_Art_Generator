type Props = {
    image: string;
    metadata: string;
  };
  
  const MintStatus = ({ image, metadata }: Props) => {
    return (
      <div className="mt-6">
        <h2 className="text-xl font-semibold text-white">🎉 Your AI-Generated Art</h2>
        <img src={image} alt="AI Art" className="rounded mt-4 border border-white" />
        <p className="mt-2 text-white">
          <strong>Metadata URL:</strong>{" "}
          <a href={metadata} target="_blank" rel="noopener noreferrer" className="text-blue-400 underline">
            View on IPFS
          </a>
        </p>
      </div>
    );
  };
  
  export default MintStatus;
  