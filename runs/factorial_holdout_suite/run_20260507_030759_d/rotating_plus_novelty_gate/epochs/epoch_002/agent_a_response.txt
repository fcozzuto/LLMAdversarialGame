def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource we can reach relatively earlier than the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = md((sx, sy), (rx, ry))
        do = md((ox, oy), (rx, ry))
        key = (ds - do, ds, rx, ry)  # deterministic
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_ds = md((sx, sy), (tx, ty))

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = md((nx, ny), (tx, ty))
        # Opponent-based pressure: prefer moves that worsen their relative race (larger gap in our favor).
        gap = (md((ox, oy), (tx, ty)) - nds)
        # Primary: minimize our distance, Secondary: maximize relative gap, Tertiary: prefer progress.
        score = (nds, -gap, cur_ds - nds, (nx - tx) ** 2 + (ny - ty) ** 2, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]