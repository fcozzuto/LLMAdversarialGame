def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        a = abs(dx)
        b = abs(dy)
        return a if a > b else b

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    if (sx, sy) in resources:
        return [0, 0]

    best = (0, 0)
    best_val = -10**18

    # Strategy: pick a resource where we have a reach-time advantage; move to improve that advantage.
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not valid(nsx, nsy):
            continue

        # Small penalty for allowing opponent to get closer (interception pressure)
        opp_next = cheb(nsx, nsy, ox, oy)
        val = 0

        # Evaluate best resource under this candidate move
        chosen = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = cheb(nsx, nsy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If we can arrive no later, prioritize; otherwise, still choose maximal swing.
            swing = d_opp - d_self
            arrive = 1 if d_self <= d_opp else 0
            # Also prefer moves that reduce our distance to that resource.
            score = (arrive * 2000) + swing * 100 - d_self
            if score > chosen:
                chosen = score

        # If no resources, just drift away from opponent
        if resources:
            val += chosen
        else:
            val = -opp_next

        # Tie-break: keep distance from opponent (or increase if equal)
        val += opp_next * 0.5

        if val > best_val:
            best_val = val
            best = (mdx, mdy)

    return [int(best[0]), int(best[1])]