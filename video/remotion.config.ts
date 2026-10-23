import { Config } from "@remotion/cli/config";
import { existsSync } from "node:fs";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// The bundled headless shell can't load its ICU data in some sandboxed macOS
// setups; fall back to the locally installed Chrome when it's there.
const LOCAL_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
if (existsSync(LOCAL_CHROME)) {
  Config.setBrowserExecutable(LOCAL_CHROME);
}
