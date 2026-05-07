export const TIME_RANGES = [
  { label: '1h',  hours: 1 },
  { label: '6h',  hours: 6 },
  { label: '24h', hours: 24 },
  { label: 'All', hours: null },
];

export default function TimeRangeSelector({ value, onChange }) {
  return (
    <div className="time-range-selector">
      {TIME_RANGES.map(({ label, hours }) => (
        <button
          key={label}
          className={`range-btn${value === label ? ' active' : ''}`}
          onClick={() => onChange(label, hours)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
