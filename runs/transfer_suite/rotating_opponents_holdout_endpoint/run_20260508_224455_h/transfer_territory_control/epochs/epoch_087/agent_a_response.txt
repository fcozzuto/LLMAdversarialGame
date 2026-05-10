def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_bonus = 10
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # nearest unclaimed (Manhattan) for shaping
    if unclaimed:
        best_un = 10**9
        tx0, ty0 = sx, sy
        for tx, ty in unclaimed:
            d = abs(tx - sx) + abs(ty - sy)
            if d < best_un:
                best_un = d
                tx0, ty0 = tx, ty
    else:
        tx0, ty0 = sx, sy

    def adj_unclaimed(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax or ay:
                    if (x + ax, y + ay) in unclaimed:
                        return 1
        return 0

    best_score = -10**9
    best_move = [0, 0]
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -999999  # avoid blocked moves (engine would keep us)
        else:
            score = 0
            if (nx, ny) in unclaimed:
                score += 8
            score += 3 * adj_unclaimed(nx, ny)
            if (nx, ny) in selfT:
                score += 1
            if (nx, ny) in oppT:
                score -= opp_bonus  # flipping gives points, but opponent control is risky for counterclaim
            score += -0.2 * (abs(tx0 - nx) + abs(ty0 - ny))  # deterministic shaping toward frontier
            if (nx, ny) == (sx, sy):
                score -= 0.4  # discourage stalling when frontier exists
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]