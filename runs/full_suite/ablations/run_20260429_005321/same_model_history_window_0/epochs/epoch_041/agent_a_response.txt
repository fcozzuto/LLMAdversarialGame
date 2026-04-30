def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cur = (sx, sy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Choose a target resource that we can contest best.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources where we are at least as close; otherwise prefer smallest disadvantage.
            winish = 0 if ds <= do else 1
            key = (winish, ds - do, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        target = best
    else:
        target = (sx, sy)

    # Score neighbor moves.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not step_valid(nx, ny):
            continue
        # If we are already on target, prefer staying or avoiding opponent.
        d_to_target = dist((nx, ny), target)
        d_to_opp = cheb((nx, ny), (ox, oy))
        # Prefer moving closer to target; also avoid stepping adjacent to opponent.
        # Deterministic tie-break uses position.
        score = (d_to_target, -d_to_opp, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # Extra deterministic "escape" if opponent is too close and we didn't avoid it.
    if cheb((sx, sy), (ox, oy)) <= 1 and resources:
        # Try to maximize distance from opponent while staying valid.
        escape_best = (0, 0)
        escape_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not step_valid(nx, ny):
                continue
            d_to_opp = cheb((nx, ny), (ox, oy))
            # Keep reasonable progress to target.
            d_to_target = dist((nx, ny), target)
            score = (-d_to_opp, d_to_target, nx, ny)
            if escape_score is None or score < escape_score:
                escape_score = score
                escape_best = (dx, dy)
        best_move = escape_best

    return [best_move[0], best_move[1]]