def choose_move(observation):
    x0, y0 = observation["self_position"]
    xo, yo = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if resources:
        best = None
        for rx, ry in resources:
            ds = abs(rx - x0) + abs(ry - y0)
            do = abs(rx - xo) + abs(ry - yo)
            margin = do - ds
            key = (margin, -ds, -((rx==x0) and (ry==y0)))
            if best is None or key > best[0]:
                best = (key, (rx, ry), ds)
        tx, ty = best[1]
        best_move = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = x0 + dx, y0 + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles: 
                continue
            ds_new = abs(tx - nx) + abs(ty - ny)
            do_new = abs(tx - xo) + abs(ty - yo)
            opp_dist = abs(xo - nx) + abs(yo - ny)
            # Prefer stepping closer to target; if tied, keep farther from opponent deterministically
            score = (-ds_new, opp_dist, dx, dy, -do_new)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        if best_move is not None:
            return best_move
    # Fallback: move toward center while avoiding obstacles, else stay
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move, best_score = None, None
    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles: 
            continue
        ds_new = abs(cx - nx) + abs(cy - ny)
        opp_dist = abs(xo - nx) + abs(yo - ny)
        score = (-ds_new, opp_dist, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]