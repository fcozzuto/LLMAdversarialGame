def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inside(x, y) or (x, y) in obstacles:
            continue
        md = abs(x - ox) + abs(y - oy)
        s = -md
        if (x, y) in opp_t:
            s += 600
        if (x, y) in unclaimed:
            s += 350
        if (x, y) in resources:
            s += 120
        if (x, y) in self_t:
            s += 60
        if best is None or s > best_score:
            best = (dx, dy)
            best_score = s

    if best is None:
        return [0, 0]
    return [best[0], best[1]]