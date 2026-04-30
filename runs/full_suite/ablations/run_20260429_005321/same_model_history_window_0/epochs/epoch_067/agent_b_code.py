def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    best_r = None
    best_val = -10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 10  # prefer reaching first
        val += (10 - sd)  # closer is better
        # if both are close, slightly prefer farther from opponent to reduce contest
        if od <= sd + 1:
            val += max(0, od - sd) * 2
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    cur_sd = cheb(sx, sy, tx, ty)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    opp_now = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # proximity to target + deny opponent margin
        score = (cur_sd - nsd) * 25
        score += (opp_now - nod) * 3
        score += (20 - nsd)
        # keep away from opponent to avoid contesting path
        score += cheb(nx, ny, ox, oy) * 0.5
        # obstacle field avoidance (penalize moving adjacent)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_pen += 1
        score -= adj_pen * 2.0

        # if opponent can grab immediately, bias toward pushing away from their likely path
        if nod <= nsd:
            score -= (nsd - nod) * 8

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]