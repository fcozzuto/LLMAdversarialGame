def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    o = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = map(int, o)

    def to_set(lst):
        out = set()
        if not lst:
            return out
        for c in lst:
            try:
                out.add((int(c[0]), int(c[1])))
            except:
                pass
        return out

    obs = to_set(observation.get("obstacles"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    un = to_set(observation.get("unclaimed_cells"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # Precompute quick distance to nearest opponent territory for corner/edge play
    # (small grid; still cheap by using opponent set bounds)
    opp_list = list(opt) if opt else []
    def dist_to_opp(x, y):
        if not opp_list:
            return abs(x - ox) + abs(y - oy)
        d = 10**9
        for px, py in opp_list:
            dd = abs(x - px) + abs(y - py)
            if dd < d:
                d = dd
        return d

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        score = 0
        if (nx, ny) in un:
            score += 40
        elif (nx, ny) in opt:
            score += 90  # flipping opponent territory on entry
        elif (nx, ny) in myt:
            score += 6

        # Frontier/expansion potential: adjacent unclaimed cells
        frontier = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if inside(tx, ty) and (tx, ty) in un:
                frontier += 1
        score += 6 * frontier

        # Pressure: prefer getting closer to opponent territory
        d = dist_to_opp(nx, ny)
        score += 25 - 3 * d

        # If moving into our own territory too long without pressure, slightly discourage
        if (nx, ny) in myt and d > dist_to_opp(sx, sy):
            score -= 10

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    if best_score == -10**18:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]