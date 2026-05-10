def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    base_dist = abs(sx - ox) + abs(sy - oy)
    best = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 900  # flipping tends to be profitable
        elif (nx, ny) in unclaimed:
            score += 120
        else:
            score += -10

        if (nx, ny) in self_t:
            score += 15

        # Prefer moving toward the opponent but mainly when it helps claim unclaimed.
        nd = abs(nx - ox) + abs(ny - oy)
        score += (base_dist - nd) * 2

        # Frontier pressure: being adjacent to opponent territory + unclaimed is strong.
        adj_unclaimed = 0
        adj_opp = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in unclaimed:
                adj_unclaimed += 1
            if (ax, ay) in opp_t:
                adj_opp += 1
        score += adj_unclaimed * 8
        score += adj_opp * (40 if (nx, ny) in opp_t else 12)

        # Avoid moving into cells deep inside opponent territory unless it grants unclaimed adjacency.
        if (nx, ny) in opp_t and adj_unclaimed == 0:
            score -= 80

        # Deterministic tie-break: prefer lexicographically smaller move among equal scores.
        if score > best_score or (score == best_score and (ddx, ddy) < best):
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]