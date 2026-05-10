def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_dist(p, cells):
        if not cells:
            return 10**9
        return min(abs(p[0] - x) + abs(p[1] - y) for (x, y) in cells)

    targets_unclaimed = unclaimed
    targets_opp = opp_terr

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        p = (nx, ny)
        val = 0
        if p in self_terr:
            val += 1
        elif p in unclaimed:
            val += 3
        elif p in opp_terr:
            val += 7
        d_u = nearest_dist((nx, ny), targets_unclaimed)
        d_o = nearest_dist((nx, ny), targets_opp)
        val += -0.25 * d_u
        val += -0.15 * d_o
        if (nx, ny) in opp_terr:
            val += 0.1 * man((nx, ny), (sx, sy)) * -1  # favor direct press slightly
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move