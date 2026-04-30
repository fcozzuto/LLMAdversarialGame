def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def best_value(px, py):
        if resources:
            best = (-10**18, 10**18)
            for rx, ry in resources:
                # relative advantage: closer to resource than opponent
                v = d2(ox, oy, rx, ry) - d2(px, py, rx, ry)
                # slight preference for more immediate distance
                t = d2(px, py, rx, ry)
                if v > best[0] or (v == best[0] and t < best[1]):
                    best = (v, t)
            return best[0], best[1]
        # fallback: drift toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return -d2(px, py, int(round(cx)), int(round(cy))), 0

    # Try to pick the move that maximizes next-step relative advantage; deterministic tie-breakers.
    best_move = (0, 0)
    best_key = (-10**18, 10**18, 10**18)  # (value, dist_self, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v, ds = best_value(nx, ny)
        # tie-break: prefer smaller ds, then prefer moving (deterministic order), then lexicographic
        key = (v, ds, dx, dy)
        if key[0] > best_key[0] or (key[0] == best_key[0] and (key[1] < best_key[1] or (key[1] == best_key[1] and (dx, dy) < best_move))):
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]