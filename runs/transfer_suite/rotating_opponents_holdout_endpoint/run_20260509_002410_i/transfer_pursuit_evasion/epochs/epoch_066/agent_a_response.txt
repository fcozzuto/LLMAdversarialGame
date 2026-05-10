def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    best = None
    best_key = None

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def edge_bias(x, y):
        # Prefer sticking to one boundary when evading (evader tends to wall-run).
        dl = x
        dr = (w - 1 - x)
        db = y
        dt = (h - 1 - y)
        m = dl
        if dr < m: m = dr
        if db < m: m = db
        if dt < m: m = dt
        return m  # smaller = closer to an edge

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            d = dist2(nx, ny, ox, oy)
            if is_pursuer:
                # Chase: minimize distance, prefer moves that also approach the opponent along x/y.
                primary = d
                # Tie-break: prefer larger progress toward opponent (deterministic).
                prog = abs(nx - ox) + abs(ny - oy)
                # Also keep away from obstacles by penalizing stepping next to any obstacle.
                adj = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        tx, ty = nx + ax, ny + ay
                        if (tx, ty) in obstacles:
                            adj += 1
                key = (primary, adj, prog, dx, dy)
            else:
                # Evade: maximize distance, prefer wall-running (edge bias small), avoid obstacle adjacency.
                primary = -d
                adj = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        tx, ty = nx + ax, ny + ay
                        if (tx, ty) in obstacles:
                            adj += 1
                eb = edge_bias(nx, ny)
                # Prefer increasing separation from pursuer directionally.
                sep = (nx - ox) * (sx - ox) + (ny - oy) * (sy - oy)
                key = (primary, adj, eb, -sep, dx, dy)

            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]