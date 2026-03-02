import { useState, useEffect } from 'react'
import { IoClose } from 'react-icons/io5'
import { getDataInfo } from '../api.js'

export default function SettingsModal({ onClose }) {
  const [dataInfo, setDataInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDataInfo()
      .then(setDataInfo)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal__header">
          <h2 className="modal__title">Data Status</h2>
          <button className="modal__close" onClick={onClose}>
            <IoClose size={18} />
          </button>
        </div>

        <div className="modal__body">
          {loading && (
            <p style={{ fontSize: 13, color: 'var(--text-hint)' }}>Loading…</p>
          )}

          {!loading && !dataInfo?.loaded && (
            <div style={{ padding: '16px', background: 'var(--red-lt)', borderRadius: 'var(--radius-sm)', fontSize: 13, color: 'var(--red)' }}>
              ⚠️ No data loaded. Place a CSV at <code>backend/data/mock_data.csv</code> and restart the server.
            </div>
          )}

          {dataInfo?.loaded && (
            <div className="data-info-box">
              <div className="data-info-box__row">
                <span className="data-info-box__label">Status</span>
                <span className="data-info-box__value" style={{ color: 'var(--green)' }}>● Live</span>
              </div>
              <div className="data-info-box__row">
                <span className="data-info-box__label">Total comments</span>
                <span className="data-info-box__value">{dataInfo.total_rows.toLocaleString()}</span>
              </div>
              <div className="data-info-box__row">
                <span className="data-info-box__label">Date range</span>
                <span className="data-info-box__value">
                  {dataInfo.date_range?.start} → {dataInfo.date_range?.end}
                </span>
              </div>
              <div className="data-info-box__row">
                <span className="data-info-box__label">Platforms</span>
                <span className="data-info-box__value">{dataInfo.platforms?.join(', ')}</span>
              </div>
              <div className="data-info-box__row">
                <span className="data-info-box__label">Campaigns</span>
                <span className="data-info-box__value">{dataInfo.campaigns?.length} campaigns</span>
              </div>
              <div className="data-info-box__row">
                <span className="data-info-box__label">Accounts</span>
                <span className="data-info-box__value">{dataInfo.accounts?.join(', ')}</span>
              </div>
            </div>
          )}

          <p style={{ fontSize: 12, color: 'var(--text-hint)', marginTop: 4 }}>
            To update the dataset, replace <code>backend/data/mock_data.csv</code> and restart the server.
          </p>
        </div>

        <div className="modal__footer">
          <button className="btn-primary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  )
}
