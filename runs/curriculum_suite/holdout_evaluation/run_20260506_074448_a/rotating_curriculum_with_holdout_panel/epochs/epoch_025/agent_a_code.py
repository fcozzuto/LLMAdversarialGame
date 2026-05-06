def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            best_res = None
            for rx, ry in resources:
                ds = abs(nx - rx) + abs(ny - ry)
                do = abs(ox - rx) + abs(oy - ry)
                cand = (ds - do, ds, rx, ry)  # closer to same resource than opponent
                if best_res is None or cand < best_res:
                    best_res = cand
            # prefer stronger advantage, then shorter reach
            move_cand = (best_res[0], best_res[1], abs(dx) + abs(dy), dx, dy)
            if best is None or move_cand < best:
                best = move_cand
        if best is not None:
            return [best[3], best[4]]

    # No resources: drift toward center while avoiding obstacles
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dcen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        move_cand = (dcen, abs(dx) + abs(dy), dx, dy)
        if best is None or move_cand < best:
            best = move_cand
    return [best[2], best[3]] if best is not None else [0, 0]