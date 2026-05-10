def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles") or []
    obs = {(x, y) for x, y in obstacles if isinstance(x, int) and isinstance(y, int)}
    self_terr = {(x, y) for x, y in (observation.get("self_territory") or []) if isinstance(x, int) and isinstance(y, int)}
    opp_terr = {(x, y) for x, y in (observation.get("opponent_territory") or []) if isinstance(x, int) and isinstance(y, int)}
    unclaimed = {(x, y) for x, y in (observation.get("unclaimed_cells") or []) if isinstance(x, int) and isinstance(y, int)}

    opp_x, opp_y = w - 1, h - 1
    if opp_terr:
        opp_x = sum(x for x, y in opp_terr) // len(opp_terr)
        opp_y = sum(y for x, y in opp_terr) // len(opp_terr)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            nx, ny, dx, dy = sx, sy, 0, 0
        if (nx, ny) in unclaimed:
            base = 14
        elif (nx, ny) in opp_terr:
            base = 11
        elif (nx, ny) in self_terr:
            base = 6
        else:
            base = 7
        dist = abs(nx - opp_x) + abs(ny - opp_y)
        adj_bonus = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            tx, ty = nx + ax, ny + ay
            if inside(tx, ty) and (tx, ty) in unclaimed:
                adj_bonus += 2
        score = base + adj_bonus - dist * 0.3
        candidates.append((score, -adj_bonus, dist, dx, dy))
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    return [int(candidates[0][3]), int(candidates[0][4])]