def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation["opponent_position"]

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    def score_cell(nx, ny):
        if (nx, ny) in self_t:
            return 1 + 0.5 * adj_count(nx, ny, self_t)
        if (nx, ny) in opp_t:
            # Flipping is strong; prefer flipping with proximity to our territory and away from them.
            return 20 + 3.0 * adj_count(nx, ny, self_t) - 0.5 * adj_count(nx, ny, opp_t)
        if (nx, ny) in unclaimed:
            # Claim frontiers; bias toward unclaimed near our territory and far from opponent.
            return 6 + 2.0 * adj_count(nx, ny, self_t) + 0.5 * adj_count(nx, ny, opp_t) - 0.15 * ((nx - ox) ** 2 + (ny - oy) ** 2) ** 0.5
        # Empty but not in listed sets (rare): still consider based on closeness to opponent and frontier density.
        return 0.2 + 1.0 * adj_count(nx, ny, self_t) - 0.05 * ((nx - ox) ** 2 + (ny - oy) ** 2) ** 0.5

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = score_cell(nx, ny)
        # Tiebreak: prefer closer to opponent if values equal, otherwise deterministic order.
        if v > best_val + 1e-9:
            best_val = v
            best_move = [dx, dy]
        elif abs(v - best_val) <= 1e-9:
            curd = abs(nx - ox) + abs(ny - oy)
            bestd = abs(sx + best_move[0] - ox) + abs(sy + best_move[1] - oy)
            if curd < bestd:
                best_move = [dx, dy]
    return best_move