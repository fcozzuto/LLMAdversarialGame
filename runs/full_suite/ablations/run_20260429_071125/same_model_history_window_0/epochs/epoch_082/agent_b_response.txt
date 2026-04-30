def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]
    obst = set((x, y) for x, y in obstacles)

    deltas = [(0,0), (1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)]
    best_move = (0, 0)
    best_val = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue
        self_dist_best = -10**9
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            val = (od - sd) * 100 - sd  # prioritize taking resources opponent can't reach first
            if val > self_dist_best:
                self_dist_best = val
        if best_val is None or self_dist_best > best_val:
            best_val = self_dist_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]