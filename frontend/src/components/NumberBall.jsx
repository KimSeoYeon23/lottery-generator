const NumberBall = ({ n }) => {
  const cls = n <= 10 ? 'r1' : n <= 20 ? 'r2' : n <= 30 ? 'r3' : n <= 40 ? 'r4' : 'r5';
  return <div className={`ball ${cls}`}>{n}</div>;
};

export default NumberBall;
