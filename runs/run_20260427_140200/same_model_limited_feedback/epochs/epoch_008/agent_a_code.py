def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    # If our target list absent, just stay safe.
    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    obs_set = set((p[0], p[1]) for p in obstacles)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource to contest: maximize advantage and also proximity when opponent is closer.
    best_res = resources[0]
    best_val = -10**9
    for rx, ry in resources:
        dS = dist((sx, sy), (rx, ry))
        dO = dist((ox, oy), (rx, ry))
        # Favor resources where we are closer; if not, prefer ones we can still reach earlier by moving diagonally.
        val = (dO - dS) * 3 - dS
        # Slightly prefer interior squares (less likely to be boxed near edges/obstacles).
        val += (2 - min(rx, w - 1 - rx)) + (2 - min(ry, h - 1 - ry))
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res

    # Evaluate each move deterministically with tactical scoring.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d_before = dist((sx, sy), (tx, ty))
        d_after = dist((nx, ny), (tx, ty))
        # Lower distance to target is good.
        score = (d_before - d_after) * 10 - d_after
        # If we can reach target (or nearly), add bonus.
        if d_after == 0:
            score += 10000
        # Contest: try to also increase opponent distance to same target.
        dO_before = dist((ox, oy), (tx, ty))
        # Approximate opponent response: assume they move one step toward the target using best diagonal/orthogonal.
        possible = []
        for adx, ady in moves:
            mx, my = ox + adx, oy + ady
            if 0 <= mx < w and 0 <= my < h and (mx, my) not in obs_set:
                possible.append((mx, my))
        if possible:
            opp_best = min(possible, key=lambda p: dist(p, (tx, ty)))
            dO_after = dist(opp_best, (tx, ty))
            score += (dO_after - dO_before) * 5

        # Obstacle/edge pressure: discourage moves that reduce future options.
        open_neighbors = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obs_set:
                open_neighbors += 1
        score += open_neighbors * 0.5

        # Deterministic tie-break: prefer smaller (abs dx)+abs dy then lexicographic.
        tie = (abs(dx) + abs(dy), dx, dy)

        if score > best_score or (score == best_score and tie < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]