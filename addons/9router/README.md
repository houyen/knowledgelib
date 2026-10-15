# addon: 9router

Trỏ OpenCode / Claude Code / Gemini CLI vào [9router](http://localhost:20128/dashboard) chạy local (gộp nhiều account Antigravity/Gemini, xoay vòng + fallback). Đây là cấu hình **máy cá nhân**, không phải policy của harness — không được cài mặc định bởi `install.sh`.

```bash
bash addons/9router/setup-9router.sh   # hỏi key + mật khẩu dashboard, nhập ẩn
source ~/.zshrc
```

Muốn tách 2 bộ account chạy song song (2 instance): thêm `--multi` và đọc mục **Kiến trúc 2 instance** bên dưới.
Script idempotent, không ghi đè `opencode.json` có sẵn, không chứa bí mật. Key/mật khẩu nhập ẩn (không gõ inline `KEY=... bash ...` — sẽ lọt vào shell history). Bấm Enter bỏ qua thì script tạo file với placeholder.

## Lệnh sau khi cài

| Lệnh | Tool | Model |
|---|---|---|
| `oc-fast` | OpenCode | combo `fast` |
| `oc-smart` | OpenCode | combo `smart` |
| `oc-flash` | OpenCode | `ag/gemini-3.8-flash-high` |
| `oc-all` | OpenCode | combo `all` của **instance 2** (`--multi`, cổng 20129) |
| `claude-ag` | Claude Code | Sonnet=`smart`, Opus=`ag/claude-opus-4-6-thinking`, Haiku=`ag/gemini-3.8-flash-high` |
| `gemini-9r` | Gemini CLI | `smart` (đổi bằng `GEMINI_9R_MODEL=fast`) |

## Combo (tạo tay ở dashboard → Combos nếu không truyền mật khẩu)

- `smart` = `ag/claude-sonnet-4-6` → `ag/gemini-3.1-pro-low` → `ag/gemini-3.8-flash-high`
- `fast` = `ag/gemini-3.8-flash-high` → `ag/gemini-3.7-flash-high` → `ag/gemini-3.5-flash-high` → `smart`

9router hỗ trợ **combo lồng** và bỏ qua model lỗi để sang model kế (đã kiểm chứng). Nên `fast` cạn thì tự sang `smart` ngay trong request; OpenCode không tự đổi model, fallback chỉ nằm trong 9router.

## Kiến trúc 2 instance (tách bộ account) — `--multi`

**Vấn đề:** 9router chỉ có MỘT pool account cho mỗi provider. Combo chỉ chọn *model*, không chọn được *account*; header `x-connection-id` chỉ ghim mềm (account bị khoá thì nó tự sang account khác). Muốn cách ly quota giữa 2 bộ account thì phải chạy **2 instance**, mỗi cái một `DATA_DIR`.

| | instance 1 (`set1`) | instance 2 (`set2`) |
|---|---|---|
| Cổng | `20128` | `20129` |
| Dữ liệu | `~/.9router` | `~/.9router-set2` (qua `DATA_DIR`) |
| Account | bộ 1 | bộ 2 |
| Combo | `fast` / `smart` / … | `all` (mọi model dùng được, fallback theo thứ tự) |
| Lệnh | `oc-fast`, `oc-smart` | `oc-all` (provider OpenCode `9router-b`) |

Một `NINEROUTER_KEY` dùng được cho cả hai (bản sao DB mang theo bảng API key).

**Launcher `9router-multi`** (cài vào `~/.local/bin` bởi `setup-9router.sh --multi`):

```bash
9router-multi start|stop|restart|status [set1|set2|all]
9router-multi autostart on|off|status      # LaunchAgent macOS
```

> ⚠️ **Đừng chạy `9router` (CLI/tray) khi đang dùng multi.** `cli.js` chạy `killAllAppProcesses()` lúc khởi động và giết MỌI tiến trình 9router khác, kể cả instance ở cổng khác. Launcher spawn thẳng `app/custom-server.js` với `PORT`/`HOSTNAME`/`DATA_DIR`, bỏ bước dọn đó. Cấu hình lại qua env: `NINEROUTER_INSTANCES="name:port:datadir …"`, `NINEROUTER_APP`, `NINEROUTER_HOST`.

Mặc định server bind `127.0.0.1` (chạy bằng `9router` không cờ thì bind `0.0.0.0` = máy trong LAN truy cập được). Đổi bằng `NINEROUTER_HOST`.

### Sau khi restart máy

```bash
9router-multi autostart on      # làm MỘT lần: cài LaunchAgent com.9router-multi (RunAtLoad)
9router-multi status            # sau mỗi lần đăng nhập, phải thấy set1/set2 UP
```

- Bật autostart thì mỗi lần đăng nhập macOS tự chạy `9router-multi start`; không cần làm gì thêm.
- Chưa bật autostart, hoặc sau restart thấy `DOWN`: chạy `9router-multi start`.
- Log: `~/.9router-multi/<set>.log` (server), `~/.9router-multi/launchd.log` (LaunchAgent).
- Tắt tự chạy: `9router-multi autostart off` (server đang chạy không bị giết).
- Sau khi nâng cấp package (`npm i -g 9router@latest`): `9router-multi restart`.
- Linux: `autostart` chưa hỗ trợ — tạo `systemd --user` service chạy `9router-multi start`.
- Đã kiểm chứng: `autostart on` dựng cả hai instance; `autostart off` không giết chúng (`AbandonProcessGroup`); bật lại không sinh tiến trình thừa. **Chưa kiểm chứng bằng một lần khởi động lại máy thật.**

### Tạo bộ account thứ 2 (thủ công, một lần)

Account là OAuth nên không script hoá hết được. Sau khi instance 1 đã có đủ các account:

```bash
SRC=~/.9router; DST=~/.9router-set2
sqlite3 $SRC/db/data.sqlite ".backup '$SRC/db/backups/pre-split.sqlite'"          # sao lưu trước
mkdir -p $DST/db $DST/logs $DST/runtime
cp -p $SRC/jwt-secret $SRC/machine-id $SRC/model-catalog*.json $DST/ ; chmod 600 $DST/jwt-secret $DST/machine-id
[ -d $SRC/auth ] && cp -Rp $SRC/auth $DST/
sqlite3 $SRC/db/data.sqlite ".backup '$DST/db/data.sqlite'"
# bản sao: giữ CHỈ account của bộ 2, xoá combo + lịch sử
sqlite3 $DST/db/data.sqlite "delete from providerConnections where email not like '<email-bo-2-a>%' and email not like '<email-bo-2-b>%';
  delete from combos; delete from usageHistory; delete from requestDetails; delete from usageDaily;"
9router-multi start set2
# rồi xoá 2 account bộ 2 khỏi instance 1: dashboard :20128 → Providers → xoá (hoặc DELETE /api/providers/<id>)
bash addons/9router/setup-9router.sh --multi     # tạo combo 'all' + provider 9router-b + oc-all
```

Kiểm tra cách ly: gửi vài request vào từng cổng rồi
`sqlite3 <DATA_DIR>/db/data.sqlite "select c.email,count(*) from usageHistory u left join providerConnections c on c.id=u.connectionId group by 1"` — mỗi DB chỉ được thấy account của bộ nó.

## Bẫy đã gặp

- `agy` (Antigravity CLI) **không** trỏ được vào 9router: không có cờ base URL. Nó dùng account Antigravity riêng.
- Gemini CLI mặc định `oauth-personal` bị Google chặn và làm CLI bỏ qua `GEMINI_API_KEY`. Dùng home riêng `~/.gemini-9r` với `selectedType: gemini-api-key`.
- 9router chỉ nhận `Authorization: Bearer`, không nhận `x-goog-api-key` → cần `GEMINI_API_KEY_AUTH_MECHANISM=bearer`.
- Claude Code gọi thêm model nhỏ (Haiku slot); không đặt `ANTHROPIC_DEFAULT_HAIKU_MODEL` thì nó gửi tên `claude-haiku-*` và lỗi.
- Không `export ANTHROPIC_BASE_URL` toàn cục: sẽ chuyển cả Claude Code thật sang 9router.

## Chưa kiểm chứng

- Fallback khi hết quota **thật** (mới thử mô phỏng bằng model không tồn tại).
- Tool-use nhiều bước của Claude Code / Gemini CLI khi combo rơi sang model Gemini.
- Fallback khi hết quota thật của combo `all` (instance 2), và tự khởi động sau một lần restart máy thật.
