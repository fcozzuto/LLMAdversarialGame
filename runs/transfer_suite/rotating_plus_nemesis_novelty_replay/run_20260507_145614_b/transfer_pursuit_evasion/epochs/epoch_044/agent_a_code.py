def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    def closest_obst2(x, y):
        if not obst:
            return 10**9
        m = 10**9
        for (bx, by) in obst:
            d = dist2(x, y, bx, by)
            if d < m:
                m = d
        return m

    target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy)) if evader else min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, target[0], target[1])
        safe = free_neighbors(nx, ny)
        obst_clear = closest_obst2(nx, ny)
        # Primary: pursue/evade. Secondary: safety. Tertiary: move toward/away from a corner.
        val = (-d_opp if not evader else d_opp) + 0.35 * safe + 0.002 * obst_clear + (0.02 * (-d_tgt if evader else d_tgt))
        if best_val is None or val < best_val if not evader else val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move