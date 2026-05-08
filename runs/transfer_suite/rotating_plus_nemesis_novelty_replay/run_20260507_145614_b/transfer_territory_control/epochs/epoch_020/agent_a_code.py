def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = observation["opponent_position"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        adj_opp = max(abs(nx - ox), abs(ny - oy)) == 1

        if (nx, ny) in opp_t:
            v = 200 - 1.5 * dist_center - 0.1 * dist_opp
        elif (nx, ny) in unclaimed:
            v = 40 - dist_center - (3 if adj_opp else 0) - 0.05 * dist_opp
        elif (nx, ny) in self_t:
            v = 12 - 0.8 * dist_center - (2 if adj_opp else 0) - 0.05 * dist_opp
        else:
            v = 5 - 1.0 * dist_center - (4 if adj_opp else 0) - 0.08 * dist_opp

        if v > bestv or (v == bestv and (dx, dy) == (0, 0)):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]