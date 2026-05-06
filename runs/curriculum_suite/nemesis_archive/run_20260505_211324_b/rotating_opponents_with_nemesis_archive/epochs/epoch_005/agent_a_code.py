def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # If no resources: move to maximize distance from opponent while staying feasible
    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = manh(nx, ny, ox, oy)
            key = (-d, abs(dx) + abs(dy), dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]] if best is not None else [0, 0]

    # Opponent-aware: after our move, choose the resource where we gain most over opponent
    best_key = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Estimate opponent is trying to minimize its distance to the best available resource
        best_opp = None
        best_self = None
        for r in resources:
            rx, ry = r
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            gain = od - sd  # positive means we are closer
            # maximize gain; tie-break by smaller self distance then deterministic deltas
            k_self = (-gain, sd, od, rx, ry)
            if best_self is None or k_self < best_self:
                best_self = k_self

            # opponent's best potential is what it would chase right now
            k_opp = (sd - od, od, sd, rx, ry)  # lower means opponent is already closer; used to pick resource
            if best_opp is None or k_opp < best_opp:
                best_opp = k_opp

        # Penalize moves that reduce our absolute safety by letting opponent be too close to any resource
        # (we prefer moves that both gain and keep the best resource not immediately available to opponent)
        # Compute opponent closeness to our target resource (best_self implies chosen resource indirectly)
        # Use a cheap proxy: minimum opponent distance across resources.
        min_opp_dist = min(manh(ox, oy, r[0], r[1]) for r in resources)
        # Combine: primary best_self already encodes gain; add secondary preference for larger min_opp_dist
        combined = (best_self[0], best_self[1], -min_opp_dist, best_self[2], dx, dy, nx, ny)
        if best_key is None or combined < best_key:
            best_key = combined
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]