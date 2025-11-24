import React, { CSSProperties, memo, useMemo } from "react";

interface ImageProps {
  src: string;
  alt: string;
  className?: string;
  styles?: CSSProperties;
  width?: number | string;
  height?: number | string;
  loading?: "eager" | "lazy";
  decoding?: "async" | "auto" | "sync";
  onLoad?: () => void;
  onMouseDown?: (event: React.MouseEvent<HTMLImageElement, MouseEvent>) => void;
  onClick?: (e: React.MouseEvent<HTMLImageElement, MouseEvent>) => void;
}

const ImageComponent: React.FC<ImageProps> = ({
  src,
  alt,
  className = "",
  styles,
  width,
  height,
  loading = "lazy",
  decoding = "async",
  onMouseDown,
  onClick,
  onLoad,
}) => {
  const imageUrl = useMemo(() => src, [src]);

  const style = useMemo(() => {
    const styleObj: React.CSSProperties = {};
    if (width)
      styleObj.width = typeof width === "number" ? `${width}px` : width;
    if (height)
      styleObj.height = typeof height === "number" ? `${height}px` : height;
    return styleObj;
  }, [width, height]);

  return (
    <img
      src={imageUrl}
      alt={alt}
      className={className}
      style={Object.keys(style).length ? { ...style, ...styles } : styles}
      loading={loading}
      onLoad={onLoad}
      onMouseDown={onMouseDown}
      onClick={onClick}
      decoding={decoding}
    />
  );
};

export const Image = memo(ImageComponent);
