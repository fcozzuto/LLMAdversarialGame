def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list if p and len(p) >= 2)
    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = set((c[0], c[1]) for c in unclaimed if c and len(c) >= 2)
    self_t = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []) if p and len(p) >= 2)
    opp_t = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if not targets:
        dirs = dirs + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if targets:
            nt = min((man((nx, ny), t) for t in targets), default=0)
            toward = -nt
        else:
            toward = 0
        d_opp = man((nx, ny), (ox, oy))
        val = toward + 0.6 * d_opp
        if (nx, ny) in self_t:
            val += 0.2
        if (nx, ny) in opp_t:
            val -= 0.8
        if (dx, dy) != (0, 0) and man((sx, sy), (nx, ny)) == 2:
            val -= 0.3
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move