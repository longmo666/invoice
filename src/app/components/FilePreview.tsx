import { useState } from "react";
import { ZoomIn, ZoomOut, RotateCw, Maximize2, Printer } from "lucide-react";

interface FilePreviewProps {
  fileUrl: string;
  fileName: string;
  fileType: string;
}

export default function FilePreview({ fileUrl, fileName, fileType }: FilePreviewProps) {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 25, 50));
  const handleRotate = () => setRotation((prev) => (prev + 90) % 360);
  const handleReset = () => {
    setZoom(100);
    setRotation(0);
  };
  const handlePrint = () => {
    const printWindow = window.open(fileUrl, '_blank');
    if (printWindow) {
      printWindow.onload = () => {
        printWindow.print();
      };
    }
  };

  const isImage = fileType.startsWith('image/');
  const isPDF = fileType === 'application/pdf';

  return (
    <div className="w-full h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-card/50">
        <button
          onClick={handleZoomOut}
          disabled={zoom <= 50}
          className="p-2 rounded-lg hover:bg-accent transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          title="缩小"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-[13px] text-muted-foreground min-w-[60px] text-center">
          {zoom}%
        </span>
        <button
          onClick={handleZoomIn}
          disabled={zoom >= 200}
          className="p-2 rounded-lg hover:bg-accent transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          title="放大"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <div className="w-px h-5 bg-border mx-1" />
        <button
          onClick={handleRotate}
          className="p-2 rounded-lg hover:bg-accent transition-colors"
          title="旋转"
        >
          <RotateCw className="w-4 h-4" />
        </button>
        <button
          onClick={handleReset}
          className="p-2 rounded-lg hover:bg-accent transition-colors"
          title="重置"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <div className="w-px h-5 bg-border mx-1" />
        <button
          onClick={handlePrint}
          className="p-2 rounded-lg hover:bg-accent transition-colors"
          title="打印"
        >
          <Printer className="w-4 h-4" />
        </button>
      </div>

      {/* Preview Area */}
      <div className="flex-1 overflow-auto bg-muted/30 flex items-center justify-center p-8">
        {isImage && (
          <img
            src={fileUrl}
            alt={fileName}
            style={{
              transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
              transition: 'transform 0.2s ease',
              maxWidth: '100%',
              maxHeight: '100%',
              objectFit: 'contain',
            }}
            className="shadow-lg rounded-lg"
          />
        )}
        {isPDF && (
          <iframe
            src={fileUrl}
            title={fileName}
            style={{
              width: `${zoom}%`,
              height: `${zoom}%`,
              transform: `rotate(${rotation}deg)`,
              transition: 'all 0.2s ease',
            }}
            className="border-0 bg-white rounded-lg shadow-lg"
          />
        )}
        {!isImage && !isPDF && (
          <div className="text-center">
            <p className="text-muted-foreground">不支持预览此文件类型</p>
            <p className="text-sm text-muted-foreground/60 mt-2">{fileType}</p>
          </div>
        )}
      </div>
    </div>
  );
}
