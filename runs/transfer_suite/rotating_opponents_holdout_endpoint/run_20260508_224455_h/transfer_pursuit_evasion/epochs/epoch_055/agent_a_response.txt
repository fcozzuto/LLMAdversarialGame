def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))
    # default: pursue
    best = None
    best_sc = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def obstacle_pressure(x, y):
        # penalize being adjacent to obstacles (likely to cage yourself)
        pr = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    pr += 1
        return pr

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(moves, key=lambda d: (d[0], d[1]))  # deterministic tie-break

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        opres = obstacle_pressure(nx, ny)
        # Pursuer: minimize distance; Evader: maximize distance.
        # Small biases: avoid being adjacent to edges too much if both equal.
        edge_bias = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        if is_evader:
            sc = (d * 100) - (opres * 3) - (edge_bias * 1)
        else:
            sc = (-d * 100) - (opres * 3) - (edge_bias * 1)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        # Fallback: stay put (engine keeps us in place if invalid)
        return [0, 0]
    return best