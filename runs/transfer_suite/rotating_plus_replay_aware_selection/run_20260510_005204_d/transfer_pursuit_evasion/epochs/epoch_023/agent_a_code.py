def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role for k in ("evad", "escape", "run", "hide", "runner"))

    targets = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict) and "position" in r:
            pr = r.get("position")
            if isinstance(pr, (list, tuple)) and len(pr) >= 2:
                targets.append((int(pr[0]), int(pr[1])))
    if not targets:
        targets = [(ox, oy)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        a = abs(x1 - x2); b = abs(y1 - y2)
        return a if a > b else b

    best = None
    bestv = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dres = min(cheb(nx, ny, tx, ty) for tx, ty in targets) if targets else 0
            dop = cheb(nx, ny, ox, oy)
            v = (dres * 2 + (dop if not is_evader else -dop))
            if best is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)

    return [0, 0] if best is None else [int(best[0]), int(best[1])]