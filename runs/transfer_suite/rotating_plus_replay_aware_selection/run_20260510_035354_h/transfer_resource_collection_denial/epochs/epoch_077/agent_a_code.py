def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cd(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target: resources where we're closer than opponent, prefer larger lead; tie-break by nearer.
    best_t = res[0]
    best_key = None
    for rx, ry in res:
        sd = cd((sx, sy), (rx, ry))
        od = cd((ox, oy), (rx, ry))
        lead = od - sd  # positive => we should win the race
        key = (lead, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Prefer moves that reduce our distance to target; if equal, reduce opponent distance; if still equal, prefer toward center.
        d_self = cd((nx, ny), (tx, ty))
        d_opp = cd((ox, oy), (tx, ty))
        center = (w - 1) / 2.0, (h - 1) / 2.0
        d_center = abs(nx - center[0]) + abs(ny - center[1])
        d_center_now = abs(sx - center[0]) + abs(sy - center[1])

        # Higher is better
        score = (-d_self, -d_opp, -d_center, d_center_now == d_center)
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]