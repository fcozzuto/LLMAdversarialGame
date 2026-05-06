def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        best = min(moves, key=lambda m: (man(sx + m[0], sy + m[1], ox, oy), m[0], m[1]))
        return [int(best[0]), int(best[1])]

    # Prefer moves that give us a lead on some resource; if none, pursue best available.
    # Deterministic tie-breaking by move order.
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_for_move = None  # smallest key
        for rx, ry in res:
            du = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # lead margin: higher is better -> use negative in minimization
            margin = do - du
            # When we can reach much sooner, strongly prefer it; otherwise minimize du.
            key = (-margin, du, rx, ry)
            if best_for_move is None or key < best_for_move:
                best_for_move = key
        # overall move key: first maximize lead (via -margin in best_for_move), then du.
        overall = (best_for_move[0], best_for_move[1], dx, dy)
        if best_key is None or overall < best_key:
            best_key = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]