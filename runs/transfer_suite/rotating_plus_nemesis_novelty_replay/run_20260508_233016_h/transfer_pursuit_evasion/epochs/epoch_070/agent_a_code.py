def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in self_role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    fc = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    fcx, fcy = fc[0], fc[1]
    tcx, tcy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if is_evader:
            # Escape: maximize distance from pursuer; also bias toward far corner and away from center.
            val = dist2(nx, ny, ox, oy)
            val += 0.15 * dist2(nx, ny, fcx, fcy)
            val += 0.02 * (dist2(nx, ny, int(tcx), int(tcy)) - dist2(sx, sy, int(tcx), int(tcy)))
        else:
            # Pursue: minimize distance; slightly bias toward cornering and keeping move "direct".
            val = -dist2(nx, ny, ox, oy)
            val += 0.04 * (dist2(nx, ny, fcx, fcy) - dist2(sx, sy, fcx, fcy)) * 0.1
            # Directness: prefer moves that reduce dx/dy signs relative to opponent.
            sxn = 0 if nx == ox else (1 if nx > ox else -1)
            syn = 0 if ny == oy else (1 if ny > oy else -1)
            rsx = 0 if sx == ox else (1 if sx > ox else -1)
            rsy = 0 if sy == oy else (1 if sy > oy else -1)
            val += 0.02 * (1 if (sxn == rsx or (nx == ox)) else 0) + 0.02 * (1 if (syn == rsy or (ny == oy)) else 0)

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]