def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_opp(x, y):
        for ax, ay in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
            if (x + ax, y + ay) in opp_t:
                return True
        return False

    def score_cell(x, y):
        s = 0
        if (x, y) in unclaimed:
            s += 12
        if adj_opp(x, y):
            s += 7
        # Encourage moving toward opponent and away from edges a bit
        s += max(0, 6 - (abs(x - ox) + abs(y - oy)))
        s += min(x, w - 1 - x, y, h - 1 - y) * 0.2
        # Penalize staying if we can expand
        if (x, y) == (sx, sy):
            s -= 2
        return s

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]