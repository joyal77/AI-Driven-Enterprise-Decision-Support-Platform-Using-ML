import React, { useEffect, useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { getRecommendations, updateRecommendationStatus } from '../services/api';

const RetentionRecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('all');
  const [viewMode, setViewMode] = useState('grouped'); // 'grouped' | 'list'
  const [expandedGroups, setExpandedGroups] = useState({});
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [bulkUpdating, setBulkUpdating] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  const handleCopyId = (id) => {
    if (!id) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(id).catch(() => fallbackCopy(id));
    } else {
      fallbackCopy(id);
    }
    setCopiedId(id);
    setTimeout(() => {
      setCopiedId(null);
    }, 2000);
  };

  const fallbackCopy = (text) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
    } catch (err) {
      console.error('Fallback copy failed', err);
    }
    document.body.removeChild(textArea);
  };

  useEffect(() => {
    fetchRecs();
  }, [page, statusFilter, viewMode]);

  const fetchRecs = async () => {
    setLoading(true);
    try {
      const limitVal = viewMode === 'grouped' ? 200 : 15;
      const data = await getRecommendations({
        status: statusFilter,
        page: viewMode === 'grouped' ? 1 : page,
        limit: limitVal,
      });
      setRecommendations(data.recommendations || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (recId, newStatus) => {
    setUpdatingId(recId);
    try {
      await updateRecommendationStatus(recId, newStatus);
      fetchRecs();
    } catch (err) {
      console.error('Error updating status:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleBulkStatusChange = async (items, newStatus) => {
    setBulkUpdating(true);
    try {
      await Promise.all(items.map((item) => updateRecommendationStatus(item.id, newStatus)));
      fetchRecs();
    } catch (err) {
      console.error('Error bulk updating status:', err);
    } finally {
      setBulkUpdating(false);
    }
  };

  const toggleGroupExpand = (strategyKey) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [strategyKey]: !(prev[strategyKey] ?? true),
    }));
  };

  const getStatusBadge = (st) => {
    switch (st) {
      case 'Accepted':
      case 'Approved':
        return <span style={{ backgroundColor: '#ecfdf5', color: '#15803d', border: '1px solid #bbf7d0', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>Accepted</span>;
      case 'Rejected':
        return <span style={{ backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>Rejected</span>;
      case 'Completed':
        return <span className="badge-low">Completed</span>;
      case 'Dismissed':
        return <span style={{ backgroundColor: '#f1f5f9', color: '#64748b', border: '1px solid #cbd5e1', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>Dismissed</span>;
      default:
        return <span className="badge-medium">Pending Review</span>;
    }
  };

  // Group recommendations by strategy description
  const groupedRecommendations = () => {
    const groupsMap = {};

    recommendations.forEach((r) => {
      const desc = r.recommendation_description;
      if (!groupsMap[desc]) {
        groupsMap[desc] = {
          strategy_description: desc,
          risk_category: r.recommendation_type,
          items: [],
          status_counts: { Pending: 0, Approved: 0, Completed: 0, Dismissed: 0 }
        };
      }
      groupsMap[desc].items.push(r);
      const st = r.status || 'Pending';
      groupsMap[desc].status_counts[st] = (groupsMap[desc].status_counts[st] || 0) + 1;
    });

    return Object.values(groupsMap);
  };

  const groups = groupedRecommendations();

  return (
    <div className="animate-fade-in">
      {/* Header Banner */}
      <div className="stat-card" style={{ marginBottom: '1.25rem', borderLeft: '5px solid #ff9900', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', color: '#0f1111', fontWeight: 900 }}>
            Amazon Customer Retention & Campaign Actions
          </h2>
          <p style={{ color: '#565959', fontSize: '0.95rem', marginTop: '0.25rem' }}>
            Automated retention strategies grouped by campaign strategy, mapping targeted actions across customer risk portfolios.
          </p>
        </div>

        {/* View Mode Switcher Buttons */}
        <div style={{ display: 'flex', gap: '0.5rem', backgroundColor: '#eaeded', padding: '0.35rem', borderRadius: '8px', border: '1px solid #d5d9d9' }}>
          <button
            type="button"
            onClick={() => setViewMode('grouped')}
            style={{
              padding: '0.45rem 0.95rem',
              borderRadius: '6px',
              border: 'none',
              fontWeight: 800,
              fontSize: '0.85rem',
              cursor: 'pointer',
              backgroundColor: viewMode === 'grouped' ? '#ff9900' : 'transparent',
              color: viewMode === 'grouped' ? '#131921' : '#565959',
              transition: 'all 0.15s ease'
            }}
          >
            📁 Grouped by Strategy ({groups.length})
          </button>
          <button
            type="button"
            onClick={() => setViewMode('list')}
            style={{
              padding: '0.45rem 0.95rem',
              borderRadius: '6px',
              border: 'none',
              fontWeight: 800,
              fontSize: '0.85rem',
              cursor: 'pointer',
              backgroundColor: viewMode === 'list' ? '#ff9900' : 'transparent',
              color: viewMode === 'list' ? '#131921' : '#565959',
              transition: 'all 0.15s ease'
            }}
          >
            📋 All Action List ({total})
          </button>
        </div>
      </div>

      {/* Status Filter Toolbar */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', backgroundColor: '#ffffff', padding: '0.85rem 1.25rem', borderRadius: '8px', border: '1px solid #d5d9d9' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#565959', alignSelf: 'center', marginRight: '0.5rem' }}>Status Filter:</span>
        {['all', 'Pending', 'Approved', 'Completed', 'Dismissed'].map((st) => (
          <button
            key={st}
            type="button"
            onClick={() => { setStatusFilter(st); setPage(1); }}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: '6px',
              border: '1px solid',
              borderColor: statusFilter === st ? '#ff9900' : '#d5d9d9',
              fontWeight: 800,
              fontSize: '0.82rem',
              cursor: 'pointer',
              backgroundColor: statusFilter === st ? '#ff9900' : '#ffffff',
              color: statusFilter === st ? '#131921' : '#565959',
              transition: 'all 0.15s ease'
            }}
          >
            {st === 'all' ? 'All Action Tasks' : st}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #d5d9d9' }}>
          <p style={{ color: '#565959' }}>Loading Amazon Retention Campaigns...</p>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="stat-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3>No Retention Actions Found</h3>
          <p style={{ color: '#565959', marginTop: '0.5rem' }}>Execute batch churn prediction or upload a new customer CSV file to generate recommendations.</p>
        </div>
      ) : viewMode === 'grouped' ? (
        /* GROUPED STRATEGY VIEW */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {groups.map((group, idx) => {
            const isExpanded = expandedGroups[idx] ?? true;
            const badgeClass =
              group.risk_category === 'High Risk'
                ? 'badge-high'
                : group.risk_category === 'Medium Risk'
                ? 'badge-medium'
                : 'badge-low';

            return (
              <div
                key={idx}
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '10px',
                  border: '1px solid #d5d9d9',
                  borderLeft: `6px solid ${group.risk_category === 'High Risk' ? '#cc0c39' : group.risk_category === 'Medium Risk' ? '#c7511f' : '#007600'}`,
                  overflow: 'hidden',
                  boxShadow: '0 2px 5px rgba(15,17,17,0.05)'
                }}
              >
                {/* Group Card Header */}
                <div style={{ padding: '1.25rem 1.5rem', backgroundColor: '#fafafa', borderBottom: isExpanded ? '1px solid #e7e7e7' : 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ flex: 1, paddingRight: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.4rem' }}>
                      <span className={badgeClass}>{group.risk_category}</span>
                      <span style={{ backgroundColor: '#232f3e', color: '#ffffff', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.78rem', fontWeight: 800 }}>
                        {group.items.length} Target {group.items.length === 1 ? 'Account' : 'Accounts'}
                      </span>
                      <div style={{ fontSize: '0.8rem', color: '#565959', display: 'flex', gap: '0.6rem', marginLeft: '0.5rem' }}>
                        <span>Pending: <strong style={{ color: '#c7511f' }}>{group.status_counts.Pending || 0}</strong></span>
                        <span>Approved: <strong style={{ color: '#1d4ed8' }}>{group.status_counts.Approved || 0}</strong></span>
                        <span>Completed: <strong style={{ color: '#007600' }}>{group.status_counts.Completed || 0}</strong></span>
                        <span>Dismissed: <strong style={{ color: '#64748b' }}>{group.status_counts.Dismissed || 0}</strong></span>
                      </div>
                    </div>
                    <h3 style={{ fontSize: '1.1rem', color: '#0f1111', fontWeight: 800, lineHeight: 1.4, margin: 0 }}>
                      🎯 Strategy: {group.strategy_description}
                    </h3>
                  </div>

                  {/* Bulk Action Buttons & Expand Toggle */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <button
                      type="button"
                      disabled={bulkUpdating}
                      onClick={() => handleBulkStatusChange(group.items, 'Approved')}
                      className="btn-amazon-gold"
                      style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', whiteSpace: 'nowrap' }}
                    >
                      Approve All ({group.items.length})
                    </button>
                    <button
                      type="button"
                      disabled={bulkUpdating}
                      onClick={() => handleBulkStatusChange(group.items, 'Completed')}
                      className="btn-amazon-orange"
                      style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', whiteSpace: 'nowrap' }}
                    >
                      Complete All ({group.items.length})
                    </button>
                    <button
                      type="button"
                      disabled={bulkUpdating}
                      onClick={() => handleBulkStatusChange(group.items, 'Dismissed')}
                      className="btn-amazon-dark"
                      style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', whiteSpace: 'nowrap' }}
                    >
                      Dismiss All ({group.items.length})
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleGroupExpand(idx)}
                      style={{
                        backgroundColor: '#ffffff',
                        border: '1px solid #d5d9d9',
                        borderRadius: '6px',
                        padding: '0.35rem 0.75rem',
                        fontSize: '0.8rem',
                        fontWeight: 800,
                        cursor: 'pointer',
                        color: '#0f1111'
                      }}
                    >
                      {isExpanded ? '▲ Hide Target Accounts' : '▼ View Target Accounts'}
                    </button>
                  </div>
                </div>

                {/* Target Accounts Table under this Strategy */}
                {isExpanded && (
                  <div style={{ padding: '0.5rem 1rem 1rem 1rem' }}>
                    <table className="data-table" style={{ margin: 0 }}>
                      <thead>
                        <tr>
                          <th>Target Account ID</th>
                          <th>Membership</th>
                          <th>Preferred Department</th>
                          <th>Task Status</th>
                          <th>Action Options</th>
                        </tr>
                      </thead>
                      <tbody>
                        {group.items.map((r) => (
                          <tr key={r.id}>
                            <td>
                              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '3px' }}>
                                <button
                                  type="button"
                                  onClick={() => handleCopyId(r.source_customer_id)}
                                  className={`btn-copy-mini ${copiedId === r.source_customer_id ? 'copied' : ''}`}
                                  title={`Copy Customer ID: ${r.source_customer_id}`}
                                >
                                  {copiedId === r.source_customer_id ? <Check size={10} /> : <Copy size={10} />}
                                  <span>{copiedId === r.source_customer_id ? 'Copied' : 'Copy ID'}</span>
                                </button>
                                <strong style={{ color: '#007185' }}>{r.source_customer_id}</strong>
                              </div>
                            </td>
                            <td>
                              {r.membership_status || 'Standard'}
                            </td>
                            <td>{r.preferred_category || 'General'}</td>
                            <td>{getStatusBadge(r.status)}</td>
                            <td>
                              <div style={{ display: 'flex', gap: '0.35rem' }}>
                                {r.status !== 'Approved' && (
                                  <button
                                    type="button"
                                    disabled={updatingId === r.id}
                                    onClick={() => handleStatusChange(r.id, 'Approved')}
                                    className="btn-amazon-gold"
                                    style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                                  >
                                    Approve
                                  </button>
                                )}
                                {r.status !== 'Completed' && (
                                  <button
                                    type="button"
                                    disabled={updatingId === r.id}
                                    onClick={() => handleStatusChange(r.id, 'Completed')}
                                    className="btn-amazon-orange"
                                    style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                                  >
                                    Complete
                                  </button>
                                )}
                                {r.status !== 'Dismissed' && (
                                  <button
                                    type="button"
                                    disabled={updatingId === r.id}
                                    onClick={() => handleStatusChange(r.id, 'Dismissed')}
                                    className="btn-amazon-dark"
                                    style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                                  >
                                    Dismiss
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        /* DETAILED FLAT LIST VIEW */
        <table className="data-table">
          <thead>
            <tr>
              <th>Account ID</th>
              <th>Membership</th>
              <th>Risk Category</th>
              <th>Recommended Retention Strategy</th>
              <th>Status</th>
              <th>Update Task Status</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((r) => (
              <tr key={r.id}>
                <td>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '3px' }}>
                    <button
                      type="button"
                      onClick={() => handleCopyId(r.source_customer_id)}
                      className={`btn-copy-mini ${copiedId === r.source_customer_id ? 'copied' : ''}`}
                      title={`Copy Customer ID: ${r.source_customer_id}`}
                    >
                      {copiedId === r.source_customer_id ? <Check size={10} /> : <Copy size={10} />}
                      <span>{copiedId === r.source_customer_id ? 'Copied' : 'Copy ID'}</span>
                    </button>
                    <strong style={{ color: '#007185' }}>{r.source_customer_id}</strong>
                  </div>
                </td>
                <td>
                  {r.membership_status || 'Standard'}
                </td>
                <td>
                  <span className={r.recommendation_type === 'High Risk' ? 'badge-high' : r.recommendation_type === 'Medium Risk' ? 'badge-medium' : 'badge-low'}>
                    {r.recommendation_type}
                  </span>
                </td>
                <td style={{ maxWidth: '420px', lineHeight: 1.4 }}>{r.recommendation_description}</td>
                <td>{getStatusBadge(r.status)}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.35rem' }}>
                    {r.status !== 'Approved' && (
                      <button
                        type="button"
                        disabled={updatingId === r.id}
                        onClick={() => handleStatusChange(r.id, 'Approved')}
                        className="btn-amazon-gold"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                      >
                        Approve
                      </button>
                    )}
                    {r.status !== 'Completed' && (
                      <button
                        type="button"
                        disabled={updatingId === r.id}
                        onClick={() => handleStatusChange(r.id, 'Completed')}
                        className="btn-amazon-orange"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                      >
                        Complete
                      </button>
                    )}
                    {r.status !== 'Dismissed' && (
                      <button
                        type="button"
                        disabled={updatingId === r.id}
                        onClick={() => handleStatusChange(r.id, 'Dismissed')}
                        className="btn-amazon-dark"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                      >
                        Dismiss
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Pagination for list view */}
      {viewMode === 'list' && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', backgroundColor: '#ffffff', padding: '0.85rem 1.25rem', borderRadius: '8px', border: '1px solid #d5d9d9' }}>
          <span style={{ fontSize: '0.85rem', color: '#565959' }}>
            Showing Page <strong>{page}</strong> of {Math.ceil(total / 15)} (Total <strong>{total?.toLocaleString()}</strong> action items)
          </span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="btn-amazon-dark" style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem' }}>
              ◀ Previous
            </button>
            <button disabled={page * 15 >= total} onClick={() => setPage(page + 1)} className="btn-amazon-dark" style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem' }}>
              Next ▶
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RetentionRecommendationsPage;
