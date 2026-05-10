def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d = dist2(nx, ny, ox, oy)
        center_pen = dist2(nx, ny, cx, cy) * 0.001

        # one-step obstacle awareness: penalize moves that leave fewer options (locally)
        options = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in blocked:
                options += 1
        scarcity_pen = (9 - options) * 0.2

        # Score: pursuer wants smaller distance, evader wants larger distance.
        if is_evader:
            val = (-d) - center_pen - scarcity_pen
        else:
            val = d + center_pen + scarcity_pen

        if best is None:
            best, best_val = (dx, dy), val
        else:
            # deterministic tie-break: prefer smaller |dx|+|dy|, then prefer [0,0], then stable order by moves list
            if (is_evader and val < best_val) or ((not is_evader) and val < best_val):
                best, best_val = (dx, dy), val
            elif val == best_val:
                cur = abs(dx) + abs(dy)
                prev = abs(best[0]) + abs(best[1])
                if cur < prev or (cur == prev and (dx, dy) == (0, 0)):
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]