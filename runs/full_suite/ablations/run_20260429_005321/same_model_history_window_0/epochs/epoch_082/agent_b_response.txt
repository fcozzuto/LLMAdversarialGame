def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer not to stay if movement helps.
    if resources:
        # Choose closest resource; tie-break by (x,y)
        best = None
        bestd = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            key = (d, rx, ry)
            if best is None or key < best:
                best = key
                target = (rx, ry)
                bestd = d
        tx, ty = target
        # Evaluate candidate moves toward target while avoiding obstacles/out of bounds
        best_move = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            # distance to target; tie-break to be deterministic
            nd = abs(tx - nx) + abs(ty - ny)
            # slight preference for moving (reduce dx=dy=0), then prefer diagonal when equal
            move_score = (nd, dx == 0 and dy == 0, 0 if (dx != 0 and dy != 0) else 1, dx, dy)
            if best_key is None or move_score < best_key:
                best_key = move_score
                best_move = [dx, dy]
        if best_move is not None:
            return best_move

    # If no resources (or all blocked), move toward opponent while avoiding obstacles/out of bounds
    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    cand = []
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        dist = abs(ox - nx) + abs(oy - ny)
        # Prefer reducing distance; tie-break deterministically
        cand.append((dist, ddx == 0 and ddy == 0, 0 if (ddx != 0 and ddy != 0) else 1, ddx, ddy, [ddx, ddy]))
    if cand:
        cand.sort()
        return cand[0][-1]
    return [0, 0]