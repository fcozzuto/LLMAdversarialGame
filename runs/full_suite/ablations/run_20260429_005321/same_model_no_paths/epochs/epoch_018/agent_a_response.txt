def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # If on a resource, stay (engine should allow resource pickup without extra move)
    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            val = cheb(nx, ny, ox, oy)  # maximize distance from opponent
            if val > best[2]:
                best = (dx, dy, val)
        return [best[0], best[1]]

    # Score potential moves by targeting best resource for us:
    # Prefer resources where we are closer than opponent (positive advantage),
    # else reduce opponent's lead for their closest resource.
    best_move = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # compute best target at this candidate position
        local_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer
            # also slightly prefer being near resources overall to prevent oscillation
            val = (adv * 1000) - ds
            if val > local_best:
                local_best = val
        # If we can't get ahead, focus on minimizing the opponent's closest-resource advantage
        # (approximate by comparing to the overall best target for opponent)
        # This is naturally handled by the loop above, but add a small tie-breaker:
        # prefer staying closer to the resource where opponent is currently closest.
        opp_min = None
        for rx, ry in resources:
            do = cheb(ox, oy, rx, ry)
            if opp_min is None or do < opp_min:
                opp_min = do
        if opp_min is None:
            opp_min = 0
        # tie-break: larger cheb distance from opponent (helps if values equal)
        tie = cheb(nx, ny, ox, oy)
        score = local_best + tie * 0.01 - (cheb(nx, ny, sx, sy)) * 0.001
        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [best_move[0], best_move[1]]