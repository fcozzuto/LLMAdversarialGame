def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def obstacle_neighbors(nx, ny):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obs:
                    c += 1
        return c

    best_dx, best_dy = 0, 0
    if "pursuer" in role:
        best_val = None  # minimize
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            v += 0.25 * obstacle_neighbors(nx, ny)
            v += 0.05 * (1 if dx == 0 and dy == 0 else 0)
            if best_val is None or v < best_val:
                best_val = v
                best_dx, best_dy = dx, dy
    else:
        # evader: maximize distance, prefer edges when safe
        best_val = None  # maximize
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -dist2(nx, ny, ox, oy)
            v -= 0.25 * obstacle_neighbors(nx, ny)
            on_edge = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
            v += 0.08 * on_edge
            # mild preference to keep moving away in x/y sign
            v += 0.03 * (1 if (dx != 0 and (nx - ox) * (sx - ox) > 0) or (dx == 0) else 0)
            v += 0.03 * (1 if (dy != 0 and (ny - oy) * (sy - oy) > 0) or (dy == 0) else 0)
            if best_val is None or v > best_val:
                best_val = v
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]