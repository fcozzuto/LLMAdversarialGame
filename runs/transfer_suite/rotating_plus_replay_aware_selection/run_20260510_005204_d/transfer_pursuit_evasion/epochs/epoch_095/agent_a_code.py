def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role_s = str(observation.get("self_role", "")).lower()
    role_o = str(observation.get("opponent_role", "")).lower()
    env = str(observation.get("environment_name", "")).lower()

    def is_evader(r):
        r = (r or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evade" in r) or ("escape" in r)

    self_evader = is_evader(role_s) or any(k in env for k in ("evader", "runner", "evade", "escape"))

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ok = inb(nx, ny) and ((nx, ny) not in blocked or (dx == 0 and dy == 0))
        if not ok:
            continue
        val = d2(nx, ny)
        score = -val if self_evader else val
        if best is None or score > best_val:
            best_val = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]