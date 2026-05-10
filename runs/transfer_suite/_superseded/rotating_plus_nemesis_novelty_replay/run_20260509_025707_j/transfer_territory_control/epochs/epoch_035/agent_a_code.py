def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    opp_terr = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # deterministic order

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def is_adj_to_opp(x, y):
        return ((x+1, y) in opp_terr or (x-1, y) in opp_terr or (x, y+1) in opp_terr or (x, y-1) in opp_terr)

    best = dirs[0]
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_terr:
            score += 100000
        if is_adj_to_opp(nx, ny):
            score += 5000
        score += -(abs(nx - ox) + abs(ny - oy))  # move towards opponent
        score += -(abs(nx - sx) + abs(ny - sy)) * 0  # keep deterministic structure
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best