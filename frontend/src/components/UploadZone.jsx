import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const UploadZone = ({ onUpload, isLoading }) => {
  const [dragOver, setDragOver] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) onUpload(acceptedFiles[0]);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: isLoading,
    onDragEnter: () => setDragOver(true),
    onDragLeave: () => setDragOver(false),
    onDropAccepted: () => setDragOver(false),
  });

  return (
    <div
      {...getRootProps()}
      className={`upload-zone ${dragOver ? 'drag-over' : ''} ${isLoading ? 'loading' : ''}`}
    >
      <input {...getInputProps()} />
      <div className="upload-icon">⚖️</div>
      {isLoading ? (
        <p>Processing document...</p>
      ) : (
        <>
          <p className="upload-title">Drop your legal document here</p>
          <p className="upload-subtitle">Supports PDF and DOCX · Max 50MB</p>
          <button className="upload-btn">Choose File</button>
        </>
      )}
    </div>
  );
};

export default UploadZone;
