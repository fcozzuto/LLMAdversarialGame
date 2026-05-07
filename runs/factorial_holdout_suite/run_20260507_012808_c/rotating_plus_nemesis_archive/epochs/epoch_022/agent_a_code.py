def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If we're already on a resource, prefer staying (collection handled by env)
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    def score_cell(nx, ny):
        # Lower is better (min): prioritize stealing resources (my distance < opp distance),
        # then prefer closer resource overall, then prefer cells that don't give opponent too good access.
        best = None
        my_opp_sep = cheb(nx, ny, ox, oy)
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # adv: negative means we are closer than opponent; strong priority
            adv = my_d - opp_d
            # how quickly opponent could reach relative to us at next step
            opp_to_me = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
            # avoid moving near obstacles indirectly by penalizing adjacency
            adj_block = 0
            for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in occ:
                    adj_block += 1
            val = (adv, my_d, opp_to_me, -my_opp_sep, adj_block, rx, ry)
            if best is None or val < best:
                best = val
        return best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Deterministic tie-breaking order given by deltas sequence
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue
        val = score_cell(nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move