def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**6
        if (nx, ny) in opp_terr:
            # flipping on entry is enabled; prioritize immediate conquest
            return 100000 - (abs(ox - nx) + abs(oy - ny))
        if (nx, ny) in self_terr:
            # stay/extend slightly toward center to avoid being trapped
            return 1000 - (abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny))
        if (nx, ny) in unclaimed:
            # prefer unclaimed edge/corners and closer targets
            edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            bias = 200 if edge else 0
            # encourage moving toward opponent to create contact while still taking territory
            return 2000 + bias - (abs(sx - nx) + abs(sy - ny)) + (abs(ox - nx) + abs(oy - ny)) * 0.01
        # neutral cells: minimal move unless they help get closer to unclaimed/opp
        return 0.0

    # Primary target set: unclaimed edge cells, else all unclaimed; fallback to opponent territory (to reach borders)
    target_cells = []
    if unclaimed:
        edge_unclaimed = [c for c in unclaimed if c[0] in (0, w - 1) or c[1] in (0, h - 1)]
        target_cells = edge_unclaimed if edge_unclaimed else list(unclaimed)
    elif opp_terr:
        target_cells = list(opp_terr)
    else:
        target_cells = [(ox, oy)]

    # Deterministic heuristic: choose move that maximizes (cell score) and secondarily reduces distance to nearest target
    best_move = [0, 0]
    best_val = -10**18
    best_dist = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = score_cell(nx, ny)
        # distance-to-nearest target
        dmin = 10**9
        for tx, ty in target_cells[:16]:  # small deterministic cap
            d = abs(tx - nx) + abs(ty - ny)
            if d < dmin:
                dmin = d
        # turn into comparable scalar
        val2 = val - dmin * 0.1
        if val2 > best_val or (val2 == best_val and dmin < best_dist):
            best_val = val2
            best_dist = dmin
            best_move = [dx, dy]

    return best_move