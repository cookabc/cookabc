# Small, finished tools for the Mac and the editor.

Menu bar apps in Swift, VS Code extensions and web utilities in TypeScript —
local-first, pixel-clean, MIT. I keep the scope small so the finish can be real.

## On the menu bar

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/cookabc/vitals"><img src="https://raw.githubusercontent.com/cookabc/vitals/main/docs/images/overview.png" alt="Vitals pixel dashboard: CPU, GPU, memory, network, disk, battery and system on one dark panel" width="100%"></a><br><br>
      <b><a href="https://github.com/cookabc/vitals">Vitals</a></b> — a system monitor that lives only in the menu bar. A live CPU mini-curve sits in the bar itself; a pixel dashboard behind it covers CPU, GPU, memory, network, disk, battery and processes. Swift 6, macOS 26+.
    </td>
    <td width="50%" valign="top">
      <a href="https://github.com/cookabc/ai-toolbox"><img src="https://raw.githubusercontent.com/cookabc/ai-toolbox/main/docs/images/hero.png" alt="AI Toolbox hero: Codex and Claude Code usage and provider configuration in a pixel-styled menu bar panel" width="100%"></a><br><br>
      <b><a href="https://github.com/cookabc/ai-toolbox">AI Toolbox</a></b> — local usage, trends and provider switching for Codex &amp; Claude Code, in a pixel-styled panel. Reads this Mac's own logs; never touches a remote bill or quota. Swift 6, zero SPM dependencies, macOS 13+.
    </td>
  </tr>
</table>

## In the browser

**[zcode-inspector](https://github.com/cookabc/zcode-inspector)** — 把 `~/.zcode` 摊开看清楚：每一类东西占多少、删了会怎样，然后决定清掉哪些。扫描只读 `stat`，从不读取文件内容；零依赖，Node ≥ 22.5 即可跑。

<p align="center">
  <a href="https://github.com/cookabc/zcode-inspector"><img src="https://raw.githubusercontent.com/cookabc/zcode-inspector/main/docs/images/overview.png" alt="zcode-inspector overview: disk usage with a cleanup verdict for every category" width="500"></a>
</p>

## In the editor

- **[Python Dependencies Updater](https://marketplace.visualstudio.com/items?itemName=cookabc.python-dependencies-updater)** — inline update hints for `requirements.txt` and `pyproject.toml`; one-click updates, with a confirmation before every major bump.
- **[npm Dependencies Updater](https://marketplace.visualstudio.com/items?itemName=cookabc.npm-dependencies-updater)** — the same treatment for `package.json`.

---

`Swift` · `SwiftUI` · `TypeScript` · `Node.js` — the rest is private or still in the oven.
