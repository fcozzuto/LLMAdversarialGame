def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if best is None or d < best:
                best = d
                bestm = [mx, my]
        return bestm if best is not None else [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_val = None
    best_move = [0, 0]
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the resource that maximizes our chance to be earlier than opponent.
        # Primary: (opp_d - my_d). Secondary: prefer smaller my_d; tertiary: closer to opponent (to react to denial).
        local_best = None
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            # If we can arrive strictly earlier, boost strongly; if tied, slight boost for smaller my_d.
            earlier = (opp_d - my_d)
            val = (earlier, -my_d, -dist(nx, ny, ox, oy))
            if local_best is None or val > local_best:
                local_best = val

        if local_best is None:
            continue
        # Small preference for staying mobile: penalize not moving if value tied.
        move_pen = 0 if (mx != 0 or my != 0) else -0.01
        overall = (local_best[0], local_best[1] + move_pen, local_best[2])
        if best_val is None or overall > best_val:
            best_val = overall
            best_move = [mx, my]

    return best_move if best_move is not None else [0, 0]