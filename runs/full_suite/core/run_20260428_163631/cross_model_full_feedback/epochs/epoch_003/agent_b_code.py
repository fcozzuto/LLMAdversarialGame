def choose_move(observation):
    turn_index = observation.get("turn_index", 0)
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    moves = [(-1,-1), (0,-1), (1,-1),
             (-1, 0), (0,0), (1,0),
             (-1,1), (0,1), (1,1)]

    best = None
    best_score = -10**9

    # Prioritize resources if available
    target = None
    if resources:
        # pick closest to me and farther from opponent
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            d_me = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            score = d_opp - d_me
            if score > best_score:
                best_score = score
                target = (rx, ry)

    # Fallback target near center if no resource
    if target is None:
        target = (w//2, h//2)

    tx, ty = target
    # evaluate moves
    def score_move(nx, ny):
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        d_to_target = dist((nx, ny), (tx, ty))
        d_to_opp = dist((ox, oy), (tx, ty))
        # Prefer positions closer to target and farther from opponent
        s = -d_to_target * 2 + d_to_opp
        # discourage stepping onto opponent
        if (nx, ny) == (ox, oy):
            s -= 100
        return s

    best_mv = (0,0)
    best_s = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        s = score_move(nx, ny)
        if s > best_s:
            best_s = s
            best_mv = (dx, dy)

    dx, dy = best_mv
    return [dx, dy]