def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    nbrs8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    nbrs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_dist_to_set(x, y, S):
        if not S:
            return 999
        return min(abs(x - a) + abs(y - b) for (a, b) in S)

    # Target bias: prioritize unclaimed; otherwise attack opponent territory; otherwise drift to center.
    if unclaimed:
        goal_set = unclaimed
    elif oppT:
        goal_set = oppT
    else:
        goal_set = {(w // 2, h // 2)}

    best_move = (0, 0)
    best_score = -10**9

    # Precompute opponent adjacency set (boundary targets) to counterclaim deterministically.
    opp_adj = set()
    if oppT:
        for (ox, oy) in oppT:
            for dx, dy in nbrs4:
                nx, ny = ox + dx, oy + dy
                if inside(nx, ny) and (nx, ny) not in obst:
                    if (nx, ny) not in selfT:
                        opp_adj.add((nx, ny))
    use_opp_adj = bool(opp_adj)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            nx, ny = sx, sy
            dx, dy = 0, 0

        v = 0.0
        if (nx, ny) in oppT:
            v += 3.5  # strong counterclaim incentive
        if (nx, ny) in unclaimed:
            v += 2.0
        if (nx, ny) in selfT:
            v += 0.3

        # Boundary pressure: step into/near opponent territory edges, especially if not already ours.
        if use_opp_adj and (nx, ny) in opp_adj:
            v += 2.2

        # Distance shaping toward goal_set
        d_goal = nearest_dist_to_set(nx, ny, goal_set)
        v += -0.15 * d_goal

        # Avoid getting fully surrounded by obstacles (stay mobile)
        free_adj = 0
        for ax, ay in nbrs8:
            tx, ty = nx + ax, ny + ay
            if inside(tx, ty) and (tx, ty) not in obst:
                free_adj += 1
        v += 0.05 * free_adj

        if v > best_score or (v == best_score and (dx, dy) < best_move):
            best_score = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]