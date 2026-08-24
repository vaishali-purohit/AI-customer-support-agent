type EvidencePanelProps = {
  source_id: string;
  snippet: string;
};

// Shows the knowledge-base source and snippet that the agent used to answer a question
export const EvidencePanel = ({ source_id, snippet }: EvidencePanelProps) => {
  return (
    <div className="mt-3 rounded bg-white/60 p-2 text-xs">
      <p className="font-semibold">Source: {source_id}</p>
      <p className="mt-1 whitespace-pre-wrap opacity-90">
        {snippet.slice(0, 300)}
      </p>
    </div>
  );
};
