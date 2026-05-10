def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp_t = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    self_t = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x, y): return abs(x - ox) + abs(y - oy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        sc = 0.0
        d = manh(nx, ny)
        if (nx, ny) in opp_t:
            sc += 8.5 + 0.08 * d
        elif (nx, ny) in un:
            sc += 3.2 + 0.04 * d
        elif (nx, ny) in self_t:
            sc += 0.8 - 0.03 * d
        else:
            sc += 0.6 - 0.02 * d
        if dx == 0 and dy == 0:
            sc -= 0.2
        sc += -0.01 * (abs(nx - sx) + abs(ny - sy))
        if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)
    if best[0] < -10**8:
        return [0, 0]
    return [int(best[1]), int(best[2])]