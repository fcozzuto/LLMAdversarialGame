def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles:
            for adx, ady in [(0, 0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                nx, ny = sx + adx, sy + ady
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [adx, ady]
            return [0, 0]
        return [dx, dy]

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    dirs = [(0, 0),(1, 0),(-1, 0),(0, 1),(0, -1),(1, 1),(1, -1),(-1, 1),(-1, -1)]
    best_move = [0, 0]
    best_score = -10**18

    # Prefer moves that create a positive distance lead over the opponent towards the same resource.
    # Deterministic tiebreak: higher score, then smaller move norm, then lexicographic (dx,dy).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        local_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - myd
            # Small bias toward closer targets; stronger when we have lead.
            score = lead * 100 - myd
            # If opponent is already extremely close, penalize unless we are also close.
            if od == 0 and myd > 0:
                score -= 10000
            if score > local_best:
                local_best = score
        move_norm = abs(dx) + abs(dy)
        # Incorporate opponent proximity: avoid stepping into opponent unless it helps capture.
        opp_close_pen = 0
        if cheb(nx, ny, ox, oy) <= 1:
            opp_close_pen = 5
        total = local_best - opp_close_pen
        if (total > best_score or
            (total == best_score and (abs(dx)+abs(dy) < abs(best_move[0])+abs(best_move[1]) or
             (abs(dx)+abs(dy) == abs(best_move[0])+abs(best_move[1]) and (dx, dy) < (best_move[0], best_move[1]))))):
            best_score = total
            best_move = [dx, dy]

    # If all candidate moves were blocked, stay.
    return best_move