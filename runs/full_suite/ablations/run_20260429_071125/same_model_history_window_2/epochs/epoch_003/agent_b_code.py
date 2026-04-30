def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        best = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = md((nx, ny), (ox, oy))
            key = (d, dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # New policy: for each candidate step, score by best attainable "resource edge"
    # (how much closer we are than opponent), with a strong preference for moves that
    # put us within reach of some resource sooner, plus a small anti-stall penalty.
    res = [(r[0], r[1]) for r in resources]
    best_key = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        best_edge = -10**9
        best_our_d = 10**9
        best_opp_d = 10**9

        for rx, ry in res:
            our_d = md((nx, ny), (rx, ry))
            opp_d = md((ox, oy), (rx, ry))
            edge = opp_d - our_d  # positive means we are closer
            # Prefer resources where edge is large; also prefer smaller our_d when edge ties.
            if edge > best_edge or (edge == best_edge and our_d < best_our_d):
                best_edge = edge
                best_our_d = our_d
                best_opp_d = opp_d

        # If we can reach a resource no later than opponent (best_edge >= 0), prioritize it heavily.
        # Otherwise, still try to maximize edge, but prefer not to wander (penalize our distance).
        reach_bonus = 120 if best_edge >= 0 else 0
        score = reach_bonus + best_edge * 15 - best_our_d - (1 if (dx == 0 and dy == 0) else 0)

        # Deterministic tie-break: maximize score, then smaller dx/dy lexicographically.
        key = (-score, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]