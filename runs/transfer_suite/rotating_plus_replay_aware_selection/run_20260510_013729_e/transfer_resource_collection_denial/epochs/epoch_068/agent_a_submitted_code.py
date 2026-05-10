def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set(obstacles)

    def cell_xy(r):
        if isinstance(r, dict):
            if "position" in r:
                return r["position"][0], r["position"][1]
            if "x" in r and "y" in r:
                return r["x"], r["y"]
        return r[0], r[1]

    res_cells = [cell_xy(r) for r in resources]
    if not res_cells:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = bx - ax
        if d < 0:
            d = -d
        e = by - ay
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = (-10**30, 10**30, 10**30)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        my_d = 10**9
        op_d = 10**9
        for rx, ry in res_cells:
            d1 = man(nx, ny, rx, ry)
            d2 = man(ox, oy, rx, ry)
            if d1 < my_d or (d1 == my_d and d2 < op_d):
                my_d, op_d = d1, d2
        adv = op_d - my_d  # higher is better: we are closer to the chosen resource
        key = (adv, my_d, op_d)
        if key > best_key:
            best_key = key
            best = (dx, dy)

    return [0, 0] if best is None else [best[0], best[1]]