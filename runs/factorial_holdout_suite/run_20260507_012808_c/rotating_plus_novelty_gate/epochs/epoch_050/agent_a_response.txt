def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        tx = tx if (tx, ty) not in obstacles else sx
        ty = ty if (tx, ty) not in obstacles else sy
        resources = [(tx, ty)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    scored = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach strictly sooner; else still good if opponent is slow.
        rel = (opd - myd)
        center_bonus = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)) * 0.01
        # Deterministic tie-break: smaller coords earlier.
        scored.append((rel, center_bonus, -myd, rx, ry))
    scored.sort(reverse=True)
    _, _, _, tx, ty = scored[0]

    # Move one step toward target with obstacle avoidance (local greedy with slight detour)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; secondary: keep opponent farther; tertiary: closer to center to reduce reroutes.
        key = (-d_self, d_opp, -abs(nx - cx) - abs(ny - cy), nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]