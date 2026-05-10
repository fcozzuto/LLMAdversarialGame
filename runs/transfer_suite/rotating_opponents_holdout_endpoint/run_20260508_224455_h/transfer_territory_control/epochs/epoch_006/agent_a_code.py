def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Prefer expanding territory and taking useful unclaimed.
    center = (w / 2 - 0.5, h / 2 - 0.5)
    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))
    aggressive = 1.35 if opp_cnt >= self_cnt else 0.85

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        d_to_self = abs(x - sx) + abs(y - sy)
        d_to_opp = abs(x - ox) + abs(y - oy)
        dist_center = abs(x - center[0]) + abs(y - center[1])

        # Base: closer to us (reachable quickly).
        s = -0.8 * d_to_self

        # Owning/claiming values.
        if (x, y) in self_t:
            s += 1.2
        elif (x, y) in opp_t:
            s += 7.0 * aggressive  # flipping opponent territory
            s += 0.3 * (1 if d_to_opp < d_to_self else 0)
        elif (x, y) in unclaimed:
            s += 4.2  # unclaimed expansion
            s += 0.9 * (1 if dist_center < 6 else 0)

        # Small penalty for getting near the opponent to avoid getting blocked later.
        s -= 0.05 * d_to_opp
        return s

    # Targeting: immediate best neighbor based on cell score; if tie, deterministic tie-break.
    best = (score_cell(sx, sy), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        tb = (abs(nx - sx) + abs(ny - sy), nx, ny)  # deterministic
        # Prefer higher score; if equal, prefer smaller tie-break tuple components.
        cand = (sc, -tb[0], -tb[1], -tb[2])
        if sc > best[0] or (sc == best[0] and cand[1:] > (0, 0, 0)):
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]