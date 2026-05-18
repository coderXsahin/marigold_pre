import { useCallback, useState } from "react";
import "./ImageUpload.css";

const ACCEPT = ["image/jpeg", "image/png", "image/jpg"];

interface Props {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export default function ImageUpload({ onFileSelect, disabled }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validate = (file: File): string | null => {
    if (!ACCEPT.includes(file.type)) return "Only JPG and PNG images are allowed";
    return null;
  };

  const handleFile = useCallback(
    (file: File) => {
      const err = validate(file);
      if (err) {
        setError(err);
        setPreview(null);
        return;
      }
      setError(null);
      setPreview(URL.createObjectURL(file));
      onFileSelect(file);
    },
    [onFileSelect]
  );

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="upload-wrap">
      <label
        className={`dropzone ${dragOver ? "drag-over" : ""} ${disabled ? "disabled" : ""} ${preview ? "has-preview" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <input
          type="file"
          accept=".jpg,.jpeg,.png"
          onChange={onChange}
          disabled={disabled}
          hidden
        />
        {preview ? (
          <>
            <img src={preview} alt="Preview" className="preview" />
            <span className="change-hint">Click or drop to replace</span>
          </>
        ) : (
          <div className="dropzone-content">
            <div className="upload-illustration" aria-hidden>
              <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" strokeWidth="2" />
                <circle cx="18" cy="22" r="4" stroke="currentColor" strokeWidth="2" />
                <path d="M6 32l10-8 8 6 10-12 18 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <p className="drop-title">Drop your marigold photo here</p>
            <span className="hint">or click to browse · JPG or PNG</span>
          </div>
        )}
      </label>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
