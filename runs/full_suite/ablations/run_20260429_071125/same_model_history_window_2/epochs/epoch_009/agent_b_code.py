def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_move_towards(tx, ty):
        best = None
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            # tie-break: prefer smaller dx, then smaller dy deterministically
            key = (d, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    if not resources:
        best = None
        bestv = -10**9
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = md(nx, ny, ox, oy)
            key = (-v, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Contest if opponent is adjacent to any resource
    adj = [(rx, ry) for (rx, ry) in resources if md(ox, oy, rx, ry) == 1]
    if adj:
        tx, ty = min(adj, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))
        return best_move_towards(tx, ty)

    # Otherwise go for nearest resource, with a small preference to those that are closer to the opponent too (faster race)
    tx, ty = min(resources, key=lambda r: (md(sx, sy, r[0], r[1]) - 0.1 * md(ox, oy, r[0], r[1]), r[0], r[1]))
    return best_move_towards(tx, ty)