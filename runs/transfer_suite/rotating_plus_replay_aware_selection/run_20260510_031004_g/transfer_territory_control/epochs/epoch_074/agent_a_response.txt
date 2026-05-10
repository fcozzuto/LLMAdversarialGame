def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def center_dist(x, y):
        return abs(x - cx) + abs(y - cy)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # base preference: expand towards center, but don't suicide into opponent
        cd = center_dist(nx, ny)
        do = abs(nx - ox) + abs(ny - oy)
        ds = abs(nx - sx) + abs(ny - sy)
        score = -cd - 0.35 * do
        if (nx, ny) in opp_terr:
            score += 12.0  # flipping/stealing territory
            score += 0.15 * do  # sometimes back off after steal
        elif (nx, ny) in unclaimed:
            score += 5.0
            score -= 0.08 * ds
        elif (nx, ny) in self_terr:
            score += 1.0
        else:
            score += 0.5
        # edge strategy: if near opponent, prioritize captures on this move
        if do <= 1:
            score += 10.0 if (nx, ny) in opp_terr else -2.0
        # tie-break deterministically towards increasing (x,y) "direction" then stability
        key = (-(score), -dx, -dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]