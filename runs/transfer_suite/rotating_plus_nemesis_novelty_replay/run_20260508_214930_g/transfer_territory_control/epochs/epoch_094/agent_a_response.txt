def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Build a small deterministic "frontier" preference: unclaimed adjacent to our territory
    frontier = []
    if self_t:
        for ux, uy in unclaimed:
            for dx, dy in dirs:
                if (ux + dx, uy + dy) in self_t:
                    frontier.append((ux, uy))
                    break
    # If no frontier (early), prefer unclaimed near our position
    targets = frontier if frontier else list(unclaimed)

    # Precompute nearest useful target by Manhattan (cheap)
    def nearest_target(tx, ty, prefer_unclaimed=True):
        best = None
        bestd = 10**9
        for x, y in targets:
            d = abs(x - tx) + abs(y - ty)
            if prefer_unclaimed and (x, y) not in unclaimed:
                continue
            if d < bestd:
                bestd = d
                best = (x, y)
        return best, bestd

    # Opponent danger: cells adjacent to their territory (if we step into those lanes, we may be flipped soon)
    opp_adj = set()
    for x, y in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                opp_adj.add((nx, ny))

    best = (0, 0)
    best_score = -10**18
    base_dist_to_opp = abs(sx - ox) + abs(sy - oy)

    chosen, _ = nearest_target(sx, sy, prefer_unclaimed=True)

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            # Capture/flip opportunity
            score += 800
            score -= 3 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in unclaimed:
            score += 220
        elif (nx, ny) in self_t:
            score += 30

        # Prefer moving toward best unclaimed target
        if chosen is not None:
            score += 6 * ((abs(sx - chosen[0]) + abs(sy - chosen[1])) - (abs(nx - chosen[0]) + abs(ny - chosen[1])))

        # Avoid stepping near opponent-controlled "sweeper" lanes
        if (nx, ny) in opp_adj:
            score -= 90

        # Mild preference for advancing away from opponent to widen territory
        nd = abs(nx - ox) + abs(ny - oy)
        score += 2 * (nd - base_dist_to_opp)

        # Keep deterministic tie-break: prefer smaller dx, then dy, then staying
        cand = (score, -abs(ddx) - abs(ddy), -((ddx == 0 and ddy == 0)), -ddx, -ddy, ddx, ddy)
        if cand > (best_score, 0, 0, 0, 0, 0, 0):
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]