def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best = [0, 0]
    best_val = -10**18

    # Precompute opponent distances to resources (current turn).
    opp_dists = []
    opp_best = 10**9
    for r in resources:
        rx, ry = r[0], r[1]
        d = md(ox, oy, rx, ry)
        opp_dists.append((rx, ry, d))
        if d < opp_best:
            opp_best = d

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        my_best = 10**9
        win_count = 0
        best_gap = -10**9
        closest = 10**9

        for rx, ry, od in opp_dists:
            d = md(nx, ny, rx, ry)
            if d < my_best:
                my_best = d
            if d < closest:
                closest = d
            gap = od - d
            if gap > best_gap:
                best_gap = gap
            if d < od:
                win_count += 1

        # Prefer moves that put us ahead of opponent on multiple resources,
        # and reduce the closest race distance.
        # Add slight urgency early in game.
        urgency = 1 + (1 if turns_remaining < 24 else 0) + (1 if turns_remaining < 12 else 0)
        val = (opp_best - my_best) * (8 * urgency) + win_count * (3 * urgency) + best_gap * 2 - closest * 0.5

        if val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val:
            # Deterministic tie-break: prefer diagonal, then right, then down, then still
            cand = (abs(dx) == 1 and abs(dy) == 1, dx, dy, - (dx == 0 and dy == 0))
            cur = (abs(best[0]) == 1 and abs(best[1]) == 1, best[0], best[1], - (best[0] == 0 and best[1] == 0))
            if cand > cur:
                best = [dx, dy]

    return best