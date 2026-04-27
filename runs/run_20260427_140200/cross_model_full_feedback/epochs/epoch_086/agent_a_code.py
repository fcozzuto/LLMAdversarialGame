def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    center = (w // 2, h // 2)
    my_before = (mx, my)
    opp_pos = (ox, oy)

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        # Choose the move that maximizes our "first arrival" margin over the best reachable target.
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_free(nx, ny):
                continue
            my_after = (nx, ny)
            # Evaluate best target for this candidate move.
            local_best = -10**18
            for tx, ty in resources:
                t = (tx, ty)
                my_dist = d(my_after, t)
                opp_dist = d(opp_pos, t)
                margin = opp_dist - my_dist  # positive means we can reach first (or closer)
                # discourage moving too close to opponent unless we have strong margin
                prox = max(abs(nx - ox), abs(ny - oy))
                penalty = 0
                if prox <= 1:
                    penalty = 1.0
                # slight preference for nearer targets when margins tie
                local = margin - 0.02 * my_dist - penalty
                if local > local_best:
                    local_best = local
            # If we have any chance to beat opponent, take it; otherwise drift.
            fallback = -0.02 * d(my_after, center)
            val = local_best if local_best > -1e17 else fallback
            # Also prefer not increasing distance to opponent when no targets are competitive
            val += 0.01 * (d(my_before, opp_pos) - d(my_after, opp_pos))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No resources: head to center while keeping some distance from opponent.
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_free(nx, ny):
                continue
            my_after = (nx, ny)
            dist_center = d(my_after, center)
            prox = max(abs(nx - ox), abs(ny - oy))
            # Prefer larger prox (stay away), then center
            val = (prox * 1.5) - 0.01 * dist_center
            # If prox too small, heavily penalize
            if prox <= 1:
                val -= 3.0
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]