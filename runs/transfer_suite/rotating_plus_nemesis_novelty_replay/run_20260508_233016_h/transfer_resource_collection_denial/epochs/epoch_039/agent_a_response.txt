def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    res = [tuple(r) for r in resources]
    best = None
    best_move = (0, 0)

    # One-step lookahead: after moving, pick best resource by "reach first" vs opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moves that let us secure a resource sooner than opponent.
        # tie-break: closer to that resource; farther from opponent; slight preference toward center.
        chosen_key = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # If we can reach no later, prioritize; otherwise deprioritize.
            reach_first = 0 if myd <= opd else 1
            key = (
                reach_first,
                myd,
                -opd,
                -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2),  # mild center bias
                rx,
                ry,
            )
            if chosen_key is None or key < chosen_key:
                chosen_key = key
        # If all resources were somehow impossible (shouldn't happen), fall back.
        if chosen_key is None:
            chosen_key = (1, 10**9, 0, 0, 0, 0)
        if best is None or chosen_key < best:
            best = chosen_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]