/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// Use a locally installed Chromium when REMOTION_CHROME is set
// (e.g. in sandboxes that can't download Chrome Headless Shell).
if (process.env.REMOTION_CHROME) {
  Config.setBrowserExecutable(process.env.REMOTION_CHROME);
}
