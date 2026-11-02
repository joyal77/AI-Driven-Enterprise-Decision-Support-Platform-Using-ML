import "./SkeletonLoader.css";

export function SkeletonKpiCard() {
  return (
    <div className="skeleton-card glass-card">
      <div className="skeleton-header">
        <div className="skeleton skeleton-icon" />
        <div className="skeleton skeleton-badge" />
      </div>
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-value" />
      <div className="skeleton skeleton-subtitle" />
    </div>
  );
}

export function SkeletonChartCard() {
  return (
    <div className="skeleton-card glass-card">
      <div className="skeleton skeleton-title" style={{ width: "40%", marginBottom: "20px" }} />
      <div className="skeleton skeleton-chart" />
    </div>
  );
}

export function SkeletonTableRow() {
  return (
    <tr className="skeleton-row">
      <td><div className="skeleton skeleton-text" style={{ width: "40px" }} /></td>
      <td><div className="skeleton skeleton-text" style={{ width: "120px" }} /></td>
      <td><div className="skeleton skeleton-text" style={{ width: "80px" }} /></td>
      <td><div className="skeleton skeleton-text" style={{ width: "70px" }} /></td>
      <td><div className="skeleton skeleton-text" style={{ width: "90px" }} /></td>
      <td><div className="skeleton skeleton-text" style={{ width: "50px" }} /></td>
      <td><div className="skeleton skeleton-text" style={{ width: "100px" }} /></td>
      <td><div className="skeleton skeleton-text" style={{ width: "80px" }} /></td>
      <td><div className="skeleton skeleton-button" /></td>
    </tr>
  );
}
