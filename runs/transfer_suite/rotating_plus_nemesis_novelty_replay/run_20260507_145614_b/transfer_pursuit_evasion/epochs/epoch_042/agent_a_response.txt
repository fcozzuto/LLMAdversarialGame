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

    def corner_trap(x, y):
        near_corner = (x in (0, w - 1) and y in (0, h - 1))
        return 1 if near_corner and free_neighbors(x, y) <= 3 else 0

    best = None
    best_val = None
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        center = dist2(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
        val = (-1 if not evader else 1) * d + 0.25 * fn + (0.01 * (w + h) - 0.001 * center) - (1.0 if not evader else 0.6) * corner_trap(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dxm, dym) < best):
            best_val = val
            best = (dxm, dym)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]