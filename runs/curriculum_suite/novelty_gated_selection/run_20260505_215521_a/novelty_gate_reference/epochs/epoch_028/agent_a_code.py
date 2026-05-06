def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if res:
            # pick the single resource move that gives the best "lead"
            cur = -10**9
            for (tx, ty) in res:
                ds = md(nx, ny, tx, ty)
                do = md(ox, oy, tx, ty)
                lead = do - ds  # positive: we arrive earlier (in Manhattan)
                # discourage long chases and moves into "safe" resources by preferring larger lead
                cand = lead * 100 - ds - abs(tx - cx) - abs(ty - cy) * 0.3
                if cand > cur:
                    cur = cand
            # slight preference to keep opponent from collecting near us: bias away if we're very close behind
            dso = md(nx, ny, ox, oy)
            cur -= (1.0 / (1 + dso)) * 5
        else:
            cur = -md(nx, ny, cx, cy)
        if best_val is None or cur > best_val:
            best_val = cur
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]