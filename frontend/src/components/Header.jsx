export default function Header({ datasetName, onUploadClick }) {
  return (
    <header className="header">
      <div className="header-left">
        <div className="header-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
        </div>
        <div>
          <div className="header-title">QueryLens</div>
          <div className="header-subtitle">Conversational Business Intelligence</div>
        </div>
      </div>
      <div className="header-right">
        {datasetName && (
          <div className="dataset-badge">
            <span className="dot"></span>
            <span>{datasetName}</span>
          </div>
        )}
        <button className="upload-btn" onClick={onUploadClick} id="upload-dataset-btn" style={{ marginTop: 0, padding: "8px 20px" }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: "inline-block", marginRight: "8px", verticalAlign: "middle" }}>
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
          </svg>
          Upload Dataset
        </button>
      </div>
    </header>
  );
}
