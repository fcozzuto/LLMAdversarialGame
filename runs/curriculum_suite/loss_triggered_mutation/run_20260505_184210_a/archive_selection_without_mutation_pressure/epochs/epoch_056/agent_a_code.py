def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    if not resources:
        # Drift to center while not running into opponent
        best = None
        bestv = -10**18
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -(abs(nx - cx) + abs(ny - cy)) - 0.03 * man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Interception-style: prefer resources we can reach earlier than the opponent.
    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # immediate pickup preference
        if (nx, ny) in [tuple(r) for r in resources]:
            return [dx, dy]
        best_res_v = -10**18
        row_sweep_bias = 0.0  # detect "sweep rows": opponent tends to change x less while moving y
        if man(ox, oy, sx, sy) > 0:
            row_sweep_bias = 0.05 * (1 if ox == nx else 0)  # stay aligned in x to contest row sweeps

        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)

            # earlier arrival is strongly good; contest in same row also favored for sweep pressure
            contest = (d_op - d_me)
            same_row = 1.0 if ry == ny else 0.0
            same_x = 1.0 if rx == nx else 0.0
            center = -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.002

            # penalty if we march into opponent proximity while not winning the resource
            proximity_pen = 0.02 * man(nx, ny, ox, oy) if contest <= 0 else 0.0

            v = 2.2 * contest + 0.35 * same_row + 0.18 * same_x + center - proximity_pen + row_sweep_bias - 0.01 * d_me
            if v > best_res_v:
                best_res_v = v

        if best_res_v > bestv:
            bestv = best_res_v
            best = (dx, dy)

    return [best[0], best[1]]