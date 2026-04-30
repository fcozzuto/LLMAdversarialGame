def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_target(for_self):
        if not resources:
            return (w // 2, h // 2)
        x, y = (sx, sy) if for_self else (ox, oy)
        rem = observation["remaining_resource_count"]
        if rem <= 4:
            # endgame: grab closest
            return min(resources, key=lambda r: (dist((x, y), (r[0], r[1])), r[0], r[1]))
        # midgame: choose resource that maximizes "we are closer than opponent" advantage
        best = None
        best_key = None
        for r in resources:
            rx, ry = r[0], r[1]
            ds = dist((x, y), (rx, ry))
            do = dist(((ox, oy) if for_self else (sx, sy)), (rx, ry))
            # primary: maximize (do - ds); secondary: lower opponent distance; tertiary: deterministic by coord
            key = (-(do - ds), ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target(True)

    # candidate moves: prefer ones that reduce distance to chosen target, with obstacle avoidance
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    cd0 = dist((sx, sy), (tx, ty))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        cd1 = dist((nx, ny), (tx, ty))
        # discourage moving away from target and discourage moving closer to opponent if similar
        opp_d = dist((nx, ny), (ox, oy))
        key = (cd1 - cd0, cd1, -opp_d, dx, dy)
        candidates.append((key, dx, dy))
    if candidates:
        candidates.sort(key=lambda t: t[0])
        return [int(candidates[0][1]), int(candidates[0][2])]

    # if all blocked (shouldn't happen), stay
    return [0, 0]