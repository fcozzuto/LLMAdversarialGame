def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # If standing still is allowed, it's included via (0,0) in dirs.

    # Choose a target resource where we are relatively ahead vs opponent.
    best_target = None
    best_gap = None
    if resources:
        for r in resources:
            rs = dist((sx, sy), r)
            ro = dist((ox, oy), r)
            gap = ro - rs  # positive => we are closer
            if best_gap is None or gap > best_gap or (gap == best_gap and rs < dist((sx, sy), best_target)):
                best_gap = gap
                best_target = r

    # If not confident (we're not ahead), fallback to closest resource to us.
    if not resources:
        target = (sx, sy)
    else:
        rs = dist((sx, sy), best_target)
        ro = dist((ox, oy), best_target)
        if best_gap is None or ro <= rs:
            target = min(resources, key=lambda r: (dist((sx, sy), r), -abs(r[0] - sx)))
        else:
            target = best_target

    # Greedy step toward target, with opponent-aware scoring.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = dist((nx, ny), target)
        d_opp = dist((nx, ny), (ox, oy))
        d_target = dist((sx, sy), target)
        # Prefer reducing distance to target; also prefer being farther from opponent to avoid contest.
        score = (-d_self, d_opp, -abs(d_self - d_target))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]