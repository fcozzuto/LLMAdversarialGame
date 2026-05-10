def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def adj_opp(x, y):
        for dx, dy in dirs:
            nx, ny = x + (dx if abs(dx) <= 1 else 0), y + (dy if abs(dy) <= 1 else 0)
            if (nx, ny) in opp_t:
                return True
        return False

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            score = -10**9
        elif (nx, ny) in obstacles:
            score = -10**8
        else:
            score = 0
            if (nx, ny) in opp_t:
                score += 5000 - (abs(nx - ox) + abs(ny - oy))
            elif (nx, ny) in unclaimed:
                score += 200
                if adj_opp(nx, ny): score += 600
            elif (nx, ny) in self_t:
                score += 10
            else:
                score += 0
            # keep pressure: move toward "opponent-side"
            score += - (abs(nx - ox) + abs(ny - oy)) * 2
            # slight preference for advancing toward center
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += - (abs(nx - cx) + abs(ny - cy)) * 0.01
        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]