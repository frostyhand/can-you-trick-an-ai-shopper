import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { ASSETS } from "../assets";
import { MODELS, totalShelves } from "../data";
import { GITHUB_URL } from "../handle";
import { ACCENT, BG, INK_2 } from "../theme";
import { Page, Rise, useOutro, Words } from "../ui";

export const Hook: React.FC<{ duration: number }> = ({ duration }) => {
  const out = useOutro(duration);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      {ASSETS.hookClip ? (
        <OffthreadVideo src={staticFile(`envato/${ASSETS.hookClip}`)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      ) : (
        <AbsoluteFill style={{ background: `radial-gradient(circle at 30% 20%, #1d2a44 0%, ${BG} 70%)` }} />
      )}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(14,16,20,0.5) 0%, rgba(14,16,20,0.92) 68%)" }} />
      <Page transparent>
        <div style={{ flex: 1 }} />
        <Rise delay={4}>
          <div style={{ fontSize: 38, fontWeight: 600, color: ACCENT, letterSpacing: 1 }}>AN AI SHOPPING EXPERIMENT</div>
        </Rise>
        <Words text="I tried to trick AI shoppers." delay={8} every={5} style={{ fontSize: 112, fontWeight: 800, lineHeight: 1.02, marginTop: 24 }} />
        <Rise delay={34}>
          <div style={{ fontSize: 42, color: INK_2, marginTop: 36, lineHeight: 1.3 }}>
            {totalShelves.toLocaleString("en-US")} store shelves. {MODELS.length} AI models. 11 classic retail tricks.
          </div>
        </Rise>
        <Rise delay={50}>
          <div style={{ fontSize: 34, color: "#fff", marginTop: 30, fontWeight: 600 }}>by {GITHUB_URL}</div>
        </Rise>
        <div style={{ height: 80 }} />
      </Page>
    </AbsoluteFill>
  );
};
