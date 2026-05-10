def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    sr = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("pred" in sr) or (sr == "pursuer")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obstacle_adj(x, y):
        if (x, y) in obs:
            return 99
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    tx, ty = far_corner

    best_move, best_val = (0, 0), None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            val = -10**12 if pursuer else -10**12
        else:
            if pursuer:
                # Prefer immediate capture / largest distance reduction, avoid obstacles near the next cell.
                val = -dist2(nx, ny, ox, oy) * 100
                val += obstacle_adj(nx, ny) * (-3)
                # Small deterministic bias to reduce zigzag: align movement with opponent direction.
                vx = 1 if ox > sx else (-1 if ox < sx else 0)
                vy = 1 if oy > sy else (-1 if oy < sy else 0)
                val += (dx == vx) * 1 + (dy == vy) * 1
            else:
                # Evade: maximize distance, head toward far corner, and avoid getting cornered by nearby obstacles.
                val = dist2(nx, ny, ox, oy) * 100
                val += -dist2(nx, ny, tx, ty) * 2
                val += -obstacle_adj(nx, ny) * 5
                # Anti-zigzag: prefer moves that change at least one coordinate.
                val += (dx != 0 or dy != 0) * 1
        if best_val is None or val > best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]