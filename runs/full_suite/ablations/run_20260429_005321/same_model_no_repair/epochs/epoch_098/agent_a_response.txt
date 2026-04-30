def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    adj8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    def obstacle_risk(x, y):
        r = 0
        for dx, dy in adj8:
            if (x+dx, y+dy) in obst: r += 1
        if (x, y) in obst: r += 100
        return r

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal: return [0, 0]

    # Evaluate moves by targeting resources we can reach no later than the opponent.
    # Deterministic tie-breaks by (our_dist, -opponent_dist, rx, ry).
    best = (None, -10**18)
    scored_any = False
    for dx, dy, nx, ny in legal:
        scored_any = True
        bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we are not behind; otherwise still move toward them but less.
            behind = 1 if d_me > d_op else 0
            v = (-10*d_me) - (5*behind) + (2*d_op if behind else 0)
            # Small deterministic bias toward corners/edges by stable ordering.
            v += -0.01*(rx + ry) + 0.005*(7 - rx + 7 - ry)
            # Risk: avoid obstacle-adjacent squares and stay away from being boxed in.
            v -= 3.0 * obstacle_risk(nx, ny)
            # If we land on a resource, strongly prefer.
            if (nx, ny) == (rx, ry):
                v += 10000
            if v > bestv: bestv = v
        if resources:
            movev = bestv
        else:
            # If no resources, run to maximize distance from opponent.
            movev = cheb(nx, ny, ox, oy) - 3.0 * obstacle_risk(nx, ny)
        if movev > best[1]:
            best = ((dx, dy), movev)
        elif movev == best[1] and best[0] is not None:
            # Deterministic tie-break: prefer moves with smaller |dx|+|dy|, then lexicographic.
            ad = abs(dx) + abs(dy)
            bd = abs(best[0][0]) + abs(best[0][1])
            if ad < bd or (ad == bd and (dx, dy) < best[0]):
                best = ((dx, dy), movev)

    if not scored_any or best[0] is None: return [0, 0]
    return [best[0][0], best[0][1]]