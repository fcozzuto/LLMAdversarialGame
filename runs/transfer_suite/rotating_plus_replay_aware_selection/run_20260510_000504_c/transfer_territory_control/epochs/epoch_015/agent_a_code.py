def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox0, oy0 = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = ox0, oy0

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if (x, y) in opp_terr: return 50.0
        if (x, y) in unclaimed: return 18.0
        if (x, y) in self_terr: return 3.0
        return 0.2

    def nearest_dist_to_set(x, y, S):
        if not S: return 999
        best = 999
        for a, b in S:
            d = abs(x - a) + abs(y - b)
            if d < best: best = d
        return best

    opp_targets = opp_terr if opp_terr else {(ox, oy)}  # deterministic non-empty
    best_move = (0, 0)
    best_val = -1e18

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Prefer capturing opponent territory/unclaimed, and moving away from being countered
        val = 0.0
        val += cell_score(nx, ny)

        # Encourage expansion toward opponent side and discourage letting opponent reach our frontier
        val += 0.4 * (nearest_dist_to_set(nx, ny, unclaimed) == 0)  # tiny deterministic bump
        val += -0.08 * nearest_dist_to_set(nx, ny, opp_targets)

        # Reduce opponent proximity to unclaimed (territory counterclaim archetype)
        if unclaimed:
            od = nearest_dist_to_set(ox, oy, unclaimed)
            # If we are closer than opponent to the most valuable region, we gain tempo
            md = nearest_dist_to_set(nx, ny, unclaimed)
            val += 0.12 * (od - md)

        # Tie-break deterministically by direction preference order via dirs iteration and then coordinates
        if val > best_val + 1e-9:
            best_val = val
            best_move = (dx, dy)
        elif abs(val - best_val) <= 1e-9:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]