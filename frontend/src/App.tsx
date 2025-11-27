import { useState, useRef } from "react";
import { removeBG, replaceBG } from "./api";
import "./App.css";

function App() {
  const [fg, setFg] = useState<File | null>(null);
  const [bg, setBg] = useState<File | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fgInputRef = useRef<HTMLInputElement>(null);
  const bgInputRef = useRef<HTMLInputElement>(null);

  const handleRemove = async () => {
    if (!fg) return alert("Please upload a main image");
    setLoading(true);
    try {
      const res = await removeBG(fg);
      setResult("http://localhost:8000/" + res.output_url);
    } catch (error) {
      alert("Error processing image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReplace = async () => {
    if (!fg) return alert("Please upload the main image");
    if (!bg) return alert("Please upload background image");
    setLoading(true);
    try {
      const res = await replaceBG(fg, bg);
      setResult("http://localhost:8000/" + res.output_url);
    } catch (error) {
      alert("Error processing image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileDrop = (e: React.DragEvent, type: 'fg' | 'bg') => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      if (type === 'fg') setFg(file);
      if (type === 'bg') setBg(file);
    }
  };

  const clearAll = () => {
    setFg(null);
    setBg(null);
    setResult(null);
    if (fgInputRef.current) fgInputRef.current.value = '';
    if (bgInputRef.current) bgInputRef.current.value = '';
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">AI Background Tool</h1>
          <p className="subtitle">Remove or replace backgrounds with AI magic</p>
        </header>

        <div className="upload-section">
          <div className="upload-group">
            <h3 className="upload-title">Main Photo</h3>
            <div 
              className={`upload-area ${dragOver ? 'drag-over' : ''} ${fg ? 'has-file' : ''}`}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => handleFileDrop(e, 'fg')}
              onClick={() => fgInputRef.current?.click()}
            >
              <input
                ref={fgInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => setFg(e.target.files?.[0] || null)}
                className="hidden-input"
              />
              {fg ? (
                <div className="file-info">
                  <div className="file-icon">📷</div>
                  <span className="file-name">{fg.name}</span>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <div className="upload-icon">📁</div>
                  <p>Click or drag & drop to upload main photo</p>
                </div>
              )}
            </div>
          </div>

          <div className="upload-group">
            <h3 className="upload-title">New Background (Optional)</h3>
            <div 
              className={`upload-area ${bg ? 'has-file' : ''}`}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => handleFileDrop(e, 'bg')}
              onClick={() => bgInputRef.current?.click()}
            >
              <input
                ref={bgInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => setBg(e.target.files?.[0] || null)}
                className="hidden-input"
              />
              {bg ? (
                <div className="file-info">
                  <div className="file-icon">🎨</div>
                  <span className="file-name">{bg.name}</span>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <div className="upload-icon">🌅</div>
                  <p>Click or drag & drop background image</p>
                  <small>Required for background replacement</small>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="action-buttons">
          <button 
            className={`btn btn-primary ${loading ? 'loading' : ''}`}
            onClick={handleRemove}
            disabled={!fg || loading}
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                Processing...
              </>
            ) : (
              'Remove Background'
            )}
          </button>

          <button 
            className={`btn btn-secondary ${loading ? 'loading' : ''}`}
            onClick={handleReplace}
            disabled={!fg || !bg || loading}
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                Processing...
              </>
            ) : (
              'Replace Background'
            )}
          </button>

          <button 
            className="btn btn-outline"
            onClick={clearAll}
            disabled={loading}
          >
            Clear All
          </button>
        </div>

        {result && (
          <div className="result-section">
            <h3 className="result-title">✨ Your Result</h3>
            <div className="result-image-container">
              <img src={result} alt="Processed result" className="result-image" />
              <div className="result-actions">
                <a 
                  href={result} 
                  download="processed-image.png"
                  className="btn btn-success"
                >
                  Download Image
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;