import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { ASSETS } from "../assets";
import { totalShelves, MODELS } from "../data";
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
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(14,16,20,0.55) 0%, rgba(14,16,20,0.92) 70%)" }} />
      <Page transparent>
        <div style={{ flex: 1 }} />
        <Rise delay={4}>
          <div style={{ fontSize: 40, fontWeight: 600, color: ACCENT, letterSpacing: 1 }}>AI SHOPPER EXPERIMENT</div>
        </Rise>
        <Words text="We tried to trick AI shoppers." delay={8} every={5} style={{ fontSize: 112, fontWeight: 800, lineHeight: 1.02, marginTop: 24 }} />
        <Rise delay={30}>
          <div style={{ fontSize: 44, color: INK_2, marginTop: 40, lineHeight: 1.3 }}>
            {totalShelves.toLocaleString("en-US")} fake store shelves. {MODELS.length} AI models. 11 classic store tricks.
          </div>
        </Rise>
        <div style={{ height: 80 }} />
      </Page>
    </AbsoluteFill>
  );
};
