def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    if resources:
        best = None
        for rx, ry in resources:
            d_self = manhattan(sx, sy, rx, ry)
            d_opp = manhattan(ox, oy, rx, ry)
            # Prefer resources closer than opponent; otherwise still prefer closer overall.
            score = (d_opp - d_self, -d_self)  # maximize first, then maximize negative distance
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: drift toward center.
        tx, ty = (w // 2, h // 2)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d_to = manhattan(nx, ny, tx, ty)
            d_opp = manhattan(nx, ny, ox, oy)
            # Minimize distance to target, maximize separation from opponent.
            candidates.append((d_to, -d_opp, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [candidates[0][2], candidates[0][3]]