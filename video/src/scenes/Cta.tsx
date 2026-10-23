import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { ASSETS } from "../assets";
import { REPO_URL } from "../data";
import { ACCENT, BG, INK_2 } from "../theme";
import { Page, Rise } from "../ui";

export const Cta: React.FC = () => (
  <AbsoluteFill>
    {ASSETS.ctaClip ? (
      <OffthreadVideo src={staticFile(`envato/${ASSETS.ctaClip}`)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    ) : (
      <AbsoluteFill style={{ background: `radial-gradient(circle at 70% 80%, #1d2a44 0%, ${BG} 70%)` }} />
    )}
    <AbsoluteFill style={{ background: "rgba(14,16,20,0.82)" }} />
    <Page transparent>
      <div style={{ flex: 1 }} />
      <Rise>
        <div style={{ fontSize: 92, fontWeight: 800, lineHeight: 1.05 }}>Would you let an AI shop for you?</div>
      </Rise>
      <Rise delay={20}>
        <div style={{ fontSize: 38, color: INK_2, marginTop: 50 }}>Full study, code and data:</div>
        <div style={{ fontSize: 33, fontWeight: 700, color: ACCENT, marginTop: 10, whiteSpace: "nowrap" }}>{REPO_URL}</div>
      </Rise>
      <div style={{ height: 80 }} />
    </Page>
  </AbsoluteFill>
);
