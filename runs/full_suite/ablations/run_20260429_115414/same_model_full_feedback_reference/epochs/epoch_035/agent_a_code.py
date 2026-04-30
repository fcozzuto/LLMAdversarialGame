def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda d: (d[0]*2 + d[1], d[0], d[1]))  # deterministic tie-bias

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            # Prefer moves that make us closer to some resource than opponent (reduce gap).
            # Also tie-break by absolute closeness.
            best_gap = None
            best_abs = None
            for rx, ry in resources:
                sd = md(nx, ny, rx, ry)
                od = md(ox, oy, rx, ry)
                gap = sd - od
                if best_gap is None or gap < best_gap or (gap == best_gap and sd < best_abs):
                    best_gap = gap
                    best_abs = sd
            # Encourage resource capture (gap negative) and slight distancing from opponent if still tied.
            val = (best_gap, best_abs, md(nx, ny, ox, oy))
        else:
            # No visible resources: head toward center-ish while keeping away from opponent.
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            val = (md(int(nx), int(ny), int(cx), int(cy)), md(nx, ny, ox, oy))
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]