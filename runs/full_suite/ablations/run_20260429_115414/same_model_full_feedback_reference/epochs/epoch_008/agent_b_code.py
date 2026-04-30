def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    opp_legal = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if legal(nx, ny):
            opp_legal.append((dx, dy, nx, ny))
    my_legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            my_legal.append((dx, dy, nx, ny))
    if not my_legal:
        return [0, 0]

    # Prefer immediate winning captures; otherwise, maximize (opponent reachability - my reachability)
    best_score = -10**18
    best_move = (0, 0)
    for sdx, sdy, mx, my in my_legal:
        score = 0
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            my_d = cheb(mx, my, rx, ry)
            opp_best_d = cheb(ox, oy, rx, ry)
            # Assume opponent moves to minimize distance to this resource
            for _, _, px, py in opp_legal:
                d = cheb(px, py, rx, ry)
                if d < opp_best_d:
                    opp_best_d = d
            if my_d == 0:
                score += 220
                # If I take it now, don't penalize for opponent also being able to reach it.
                continue
            if opp_best_d == 0:
                score -= 170
            score += (opp_best_d - my_d) * 55 - my_d * 2
        # Mild preference for moving toward any resource to break ties deterministically
        if resources:
            any_d = min(cheb(mx, my, r[0], r[1]) for r in resources if (r[0], r[1]) not in obs)
            score -= any_d * 1
        if score > best_score:
            best_score = score
            best_move = (sdx, sdy)
        elif score == best_score:
            # Deterministic tie-break: keep direction with smallest |dx|+|dy| then lexicographic
            cd = abs(sdx) + abs(sdy); bd = abs(best_move[0]) + abs(best_move[1])
            if cd < bd or (cd == bd and (sdx, sdy) < best_move):
                best_move = (sdx, sdy)
    return [best_move[0], best_move[1]]