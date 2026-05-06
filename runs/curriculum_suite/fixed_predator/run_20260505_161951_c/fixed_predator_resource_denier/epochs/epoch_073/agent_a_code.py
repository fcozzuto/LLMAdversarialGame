def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        # End at far corner while dodging obstacles
        tx, ty = w - 1, h - 1
        best = [0, 0]; bestv = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Select a "denial" resource: where we are closer than opponent (or least worse)
    endgame = (len(resources) <= 4)
    target = None; bestt = -10**18
    for rx, ry in resources:
        s_d = cheb(x, y, rx, ry)
        o_d = cheb(ox, oy, rx, ry)
        # In endgame: maximize own closeness; otherwise prioritize denial/capture advantage.
        v = (-(s_d) if endgame else (o_d * 5 - s_d * 7))
        if not endgame:
            # Add a slight bonus for also being closer in manhattan sense (ties broken).
            man_s = abs(x - rx) + abs(y - ry)
            man_o = abs(ox - rx) + abs(oy - ry)
            v += (man_o - man_s) * 2
        if v > bestt:
            bestt = v; target = (rx, ry)

    rx, ry = target
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        s_d = cheb(nx, ny, rx, ry)
        o_d = cheb(ox, oy, rx, ry)

        # Evaluate move: go toward target, but also increase opponent's relative standing.
        # Penalize wasting moves that don't reduce our distance when not endgame.
        cur_s = cheb(x, y, rx, ry)
        progress = cur_s - s_d
        v = (o_d - s_d) * 50 - s_d * (6 if endgame else 3) + progress * (18 if not endgame else 8)

        # Extra: if move blocks by occupying a cell that is near many resources, prefer it.
        if not endgame:
            close_bonus = 0
            for (rrx, rry) in resources:
                if cheb(nx, ny, rrx, rry) <= 1:
                    close_bonus += 2
            v += close_bonus

        # Tie-break deterministically: prefer staying if equal value, otherwise lexicographic by (dx,dy)
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v; best = [dx, dy]

    return best