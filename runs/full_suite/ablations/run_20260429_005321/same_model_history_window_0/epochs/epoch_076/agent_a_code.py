def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((p[0], p[1]) for p in obstacles)
    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(oy - oy + 0)  # keep deterministic no-op style
            do = abs(rx - ox) + abs(ry - oy)
            key = (do - ds, -ds)  # prefer resources where we're closer than opponent
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r if best_r is not None else resources[0]
    else:
        tx, ty = (w // 2, h // 2)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs:
            nx, ny = sx, sy  # engine keeps in place; model that deterministically
            dx, dy = 0, 0
        # primary: move closer to target
        d_self = abs(tx - nx) + abs(ty - ny)
        # secondary: increase separation from opponent to reduce their contesting odds
        d_opp = abs(ox - nx) + abs(oy - ny)
        # tertiary: slightly prefer moves that reduce opponent-to-target distance (deny them)
        d_opp_to_t = abs(tx - ox) + abs(ty - oy)
        score = (-d_self, d_opp, -d_opp_to_t, -(dx*dx + dy*dy))
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]