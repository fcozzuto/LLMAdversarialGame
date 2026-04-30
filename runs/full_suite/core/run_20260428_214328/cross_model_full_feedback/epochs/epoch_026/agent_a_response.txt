def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    resources = observation.get("resources", []) or []
    rs = [(int(p[0]), int(p[1])) for p in resources]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if rs:
        my_nearest = min(rs, key=lambda r: dist((sx, sy), r))
        my_d0 = dist((sx, sy), my_nearest)
        opp_d0 = dist((ox, oy), my_nearest)
    else:
        my_nearest = None
        my_d0 = 10**9
        opp_d0 = 10**9

    # Deterministic tie-break: prefer diagonal then straight then stay by move order already sorted.
    best = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        val = 0

        # Resource pressure: prefer moves that get us closer to closest resource.
        if my_nearest is not None:
            d1 = dist((nx, ny), my_nearest)
            # Strongly prefer reducing distance; reward being at/under opponent reach for that target.
            val += (my_d0 - d1) * 20
            if d1 < my_d0:
                val += 5
            opp_d1 = dist((ox, oy), my_nearest)
            if d1 <= opp_d1:
                val += 60
            else:
                val -= (d1 - opp_d1) * 6

            # Also consider overall nearest resource to avoid local traps.
            dn = min(dist((nx, ny), r) for r in rs)
            val += (my_d0 - dn) * 5
        else:
            # No resources: drift towards the map center based on our side.
            cx, cy = (w // 2, h // 2)
            center_side = 1 if (sx + sy) > (w - 1 + h - 1) / 2 else -1
            dc = dist((nx, ny), (cx, cy))
            val += (-dc) * 8 + center_side

        # Opponent avoidance: keep some distance (but don't over-penalize).
        do = dist((nx, ny), (ox, oy))
        val += do * 1.5

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]