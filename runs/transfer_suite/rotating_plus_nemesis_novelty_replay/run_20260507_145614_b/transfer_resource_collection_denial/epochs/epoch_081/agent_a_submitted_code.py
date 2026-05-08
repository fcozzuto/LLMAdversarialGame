def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set(obstacles_list if all(isinstance(p, tuple) for p in obstacles_list) else [tuple(p) for p in obstacles_list])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def best_target():
        if not resources:
            return (w - 1) // 2, (h - 1) // 2
        tx, ty = resources[0]
        best = abs(tx - sx) + abs(ty - sy)
        for rx, ry in resources[1:]:
            d = abs(rx - sx) + abs(ry - sy)
            if d < best or (d == best and (rx, ry) < (tx, ty)):
                best = d; tx, ty = rx, ry
        return tx, ty

    tx, ty = best_target()
    prefs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    cur_best = None
    cur_step = (0, 0)
    for dx, dy in prefs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # Prefer stepping onto a resource; otherwise move toward target.
        on_res = (nx, ny) in set(resources)
        score = (0 if on_res else 1, d, abs(nx - ox) + abs(ny - oy), dx, dy)
        if cur_best is None or score < cur_best:
            cur_best = score
            cur_step = (dx, dy)

    return [int(cur_step[0]), int(cur_step[1])]