def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource that we are likely to beat soon, otherwise maximize differential.
    best_t = None
    for r in resources:
        myd = md((sx, sy), r)
        opd = md((ox, oy), r)
        # primary: how much ahead we can be (opd - myd); secondary: smaller my distance; tertiary: smaller opd
        key = (opd - myd, -myd, -opd, r[0], r[1])
        if best_t is None or key > best_t[0]:
            best_t = (key, r)
    tx, ty = best_t[1][0], best_t[1][1]

    # One-step lookahead: choose move that improves relative progress to target while avoiding obstacles.
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_after = md((nx, ny), (tx, ty))

        # Opponent response not predictable; approximate by assuming opponent moves similarly toward target next turn:
        # evaluate relative distance advantage if we get closer by our move.
        opp_after = md((ox, oy), (tx, ty))
        # Small bias: if opponent is also close, prioritize maximizing our lead after move.
        score = (opp_after - my_after, -my_after, -abs((nx - ox)) - abs((ny - oy)), -dx * dx - dy * dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]