def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate next step: prioritize collecting (distance 0), else maximize (opp_dist - self_dist_next).
    best = None
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        # compute heuristic against all resources
        best_val_for_this_move = None
        best_res_dist = 999999
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # big bonus if we land on a resource this turn
            if sd == 0:
                val = 10**6 + (od)  # always best to pick up immediately
            else:
                val = (od - sd) * 1000 - sd  # maximize being closer than opponent
            if best_val_for_this_move is None or val > best_val_for_this_move or (val == best_val_for_this_move and sd < best_res_dist):
                best_val_for_this_move = val
                best_res_dist = sd
        # tie-break: prefer more urgent (smaller best_res_dist), then prefer moves with dx,dy nearer to straight toward best target
        tie = (best_res_dist,)
        key = (best_val_for_this_move,) + tie
        if best is None or key > best:
            best = key
            best_m = [dx, dy]
    return best_m if best_m is not None else [0, 0]