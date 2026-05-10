def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer expansion and contesting: unclaimed > flipping opponent > staying in self.
    base_to_opp = abs(sx - ox) + abs(sy - oy)
    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 1200
        if (nx, ny) in opp_t:
            score += 900
        if (nx, ny) in self_t:
            score += 60

        # Move generally away from opponent when flipping is not immediate,
        # to reduce being squeezed; but move toward opponent if we can take a target.
        nd_opp = abs(nx - ox) + abs(ny - oy)
        score += (nd_opp - base_to_opp) * 6

        # Micro-heuristic: prefer moves that improve local "frontier":
        # count how many unclaimed/opp cells are adjacent.
        adj = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                    if (ax, ay) in unclaimed:
                        adj += 2
                    elif (ax, ay) in opp_t:
                        adj += 1
        score += adj * 25

        # Avoid drifting into a dead-end: if surrounded by obstacles, penalize.
        blocked = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                    blocked += 1
        score -= blocked * 12

        # Deterministic tie-break: prefer lexicographically smaller move deltas.
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]