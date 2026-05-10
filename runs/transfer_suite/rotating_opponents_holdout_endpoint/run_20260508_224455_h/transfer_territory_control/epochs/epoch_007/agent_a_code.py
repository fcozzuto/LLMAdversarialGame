def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))
    aggressive = 1.6 if opp_cnt >= self_cnt else 1.0

    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_opp_dist(x, y):
        # Small deterministic probe: min of a few candidate points on opponent boundary
        # Approx by min manhattan to opponent position and a couple opponent-claimed samples.
        best = abs(x - ox) + abs(y - oy)
        for px, py in (tuple(opp_t)[:1] if opp_t else []):
            best = min(best, abs(x - px) + abs(y - py))
        return best

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        d_self = abs(nx - sx) + abs(ny - sy)
        d_center = abs(nx - centerx) + abs(ny - centery)
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_opp_near = nearest_opp_dist(nx, ny)

        s = 0.0
        s += 1.2 * (7 - d_self)  # discourage waste; d_self is 0/1/2-ish
        s += 1.0 * (-0.06 * d_center)  # drift to center
        s += 0.18 * (-d_to_opp)        # keep some pressure

        if cell in self_t:
            s += 2.0 - 0.08 * d_center
        elif cell in unclaimed:
            s += 6.0 - 0.12 * d_center
            # If unclaimed is near opponent, prioritize counterclaim routes
            s += aggressive * (1.2 / (1 + d_opp_near))
        elif cell in opp_t:
            # flipping on entry: strongly prefer capturing when aggressive
            s += aggressive * (10.0 - 1.0 * d_to_opp)

        # Extra: avoid stepping onto cells that look trapped behind obstacles by biasing toward in-bounds freedom
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty) and (tx, ty) not in obstacles:
                free += 1
        s += 0.25 * free

        if s > best_score or (s == best_score and (dx, dy) == (0, 0)):
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]