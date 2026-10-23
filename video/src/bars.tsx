import { interpolate, useCurrentFrame } from "remotion";
import { INK, INK_2, MUTED } from "./theme";

export type BarDatum = { label: string; value: number; color: string; display?: string };

const grow = (frame: number, delay: number, length = 36) =>
  interpolate(frame, [delay, delay + length], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

/** Vertical bars in groups, with the value on top and labels underneath. */
export const ColumnGroups: React.FC<{
  groups: { title: string; subtitle?: string; bars: BarDatum[] }[];
  max: number;
  height?: number;
  delay?: number;
  unit?: string;
  barWidth?: number;
}> = ({ groups, max, height = 420, delay = 0, unit = "", barWidth = 140 }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", justifyContent: "space-around", alignItems: "flex-end" }}>
      {groups.map((g, gi) => (
        <div key={g.title} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 440 }}>
          <div style={{ display: "flex", gap: 28, alignItems: "flex-end", height, borderBottom: `3px solid ${MUTED}`, padding: "0 24px" }}>
            {g.bars.map((b, bi) => {
              const p = grow(frame, delay + gi * 30 + bi * 14);
              const h = Math.max(4, (b.value / max) * (height - 70) * p);
              return (
                <div key={b.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end", height: "100%" }}>
                  <div style={{ fontSize: 46, fontWeight: 800, color: INK, opacity: p, marginBottom: 8 }}>
                    {b.display ?? `${Math.round(b.value * p)}${unit}`}
                  </div>
                  <div style={{ width: barWidth, height: h, background: b.color, borderRadius: "12px 12px 0 0" }} />
                </div>
              );
            })}
          </div>
          <div style={{ display: "flex", gap: 28, marginTop: 10 }}>
            {g.bars.map((b) => (
              <div key={b.label} style={{ width: barWidth, textAlign: "center", fontSize: 24, color: INK_2, lineHeight: 1.2 }}>{b.label}</div>
            ))}
          </div>
          <div style={{ fontSize: 32, fontWeight: 800, marginTop: 16, textAlign: "center" }}>{g.title}</div>
          {g.subtitle && <div style={{ fontSize: 22, color: MUTED, marginTop: 4, textAlign: "center" }}>{g.subtitle}</div>}
        </div>
      ))}
    </div>
  );
};

/** Horizontal bars with a label on the left and the value at the bar's end. */
export const RowBars: React.FC<{ rows: BarDatum[]; max: number; delay?: number; labelWidth?: number; barMax?: number; unit?: string }> = ({
  rows, max, delay = 0, labelWidth = 330, barMax = 480, unit = "",
}) => {
  const frame = useCurrentFrame();
  return (
    <div>
      {rows.map((r, i) => {
        const p = grow(frame, delay + i * 18);
        return (
          <div key={r.label} style={{ display: "flex", alignItems: "center", marginTop: 26 }}>
            <div style={{ width: labelWidth, fontSize: 32, color: INK, lineHeight: 1.2, paddingRight: 18 }}>{r.label}</div>
            <div style={{ height: 64, width: Math.max(6, (r.value / max) * barMax * p), background: r.color, borderRadius: "0 14px 14px 0" }} />
            <div style={{ fontSize: 46, fontWeight: 800, marginLeft: 18, opacity: p, whiteSpace: "nowrap" }}>
              {r.display ?? `${Math.round(r.value * p)}${unit}`}
            </div>
          </div>
        );
      })}
    </div>
  );
};
