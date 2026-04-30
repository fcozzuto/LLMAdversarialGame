def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = set((p[0], p[1]) for p in obstacles)

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def score_cell(nx, ny):
        if (nx, ny) in obs_set:
            return -10**9
        best = -10**9
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            val = (do - ds) * 10 - ds
            if val > best:
                best = val
        if not resources:
            # If no resources, move away from opponent slightly
            val = dist(nx, ny, ox, oy)
            best = val
        return best

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-breaking by moves order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]