def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]
    # choose target resource deterministically with advantage vs opponent
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = max(abs(rx - sx) + abs(ry - sy) - 0, 0)
        do = max(abs(rx - ox) + abs(ry - oy) - 0, 0)
        # advantage: smaller is better (we want ds<do)
        key = (ds - do, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        target = (ox, oy)
    else:
        target = best[1]
    tx, ty = target

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # evaluate each move with greedy distance to target and avoidance of opponent/obstacles
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # invalid moves are rejected by staying in place
        # distances (chebyshev for diagonal steps)
        ds = max(abs(tx - nx), abs(ty - ny))
        do = max(abs(ox - nx), abs(oy - ny))
        # Prefer approach while staying away from opponent when too close
        opp_pen = 0
        if do <= 1:
            opp_pen = 1000
        elif do == 2:
            opp_pen = 50
        # Also discourage oscillation: prefer not to move if it doesn't improve much
        dist_now = max(abs(tx - sx), abs(ty - sy))
        stay_pen = 0 if (dx, dy) != (0, 0) else 3
        score = (opp_pen + ds * 10) - (do * 2) + stay_pen + (0 if ds <= dist_now else 0)
        # deterministic tie-break
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]