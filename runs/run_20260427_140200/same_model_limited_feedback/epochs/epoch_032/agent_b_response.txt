def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist2(a, b):
        dx = a[0]-b[0]
        dy = a[1]-b[1]
        return dx*dx + dy*dy
    def step_pos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            return sx, sy
        if (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    # Pick a deterministic target: contested/valuable resource by relative closeness
    if resources:
        best_r = None
        best_val = None
        for r in resources:
            ds = dist2((sx, sy), r)
            do = dist2((ox, oy), r)
            # Prefer resources where we're closer to secure; also defend contested spots
            val = (do - ds) - 0.05 * ds
            if best_val is None or val > best_val or (val == best_val and (r[0], r[1]) < (best_r[0], best_r[1])):
                best_val = val
                best_r = r
        target = best_r
    else:
        target = (w//2, h//2)

    # Candidate selection: minimize distance to target, with mild anti-trap vs opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = step_pos(dx, dy)
        d_t = dist2((nx, ny), target)
        d_o = dist2((nx, ny), (ox, oy))
        # If we are forcing opponent away from the target line, increase opponent distance slightly
        score = -d_t + 0.03 * d_o
        # Deterministic tie-break
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]