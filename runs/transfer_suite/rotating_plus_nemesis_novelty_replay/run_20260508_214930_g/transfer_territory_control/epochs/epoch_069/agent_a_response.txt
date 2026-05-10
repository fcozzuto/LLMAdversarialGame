def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a deterministic goal: nearest unclaimed, else nearest opponent territory cell.
    goal = None
    if unclaimed:
        bestd = 10**9
        best = None
        for x, y in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd or (d == bestd and (y, x) < (best[1], best[0])):
                bestd = d
                best = (x, y)
        goal = best
    else:
        pool = list(opp_t) if opp_t else [(ox, oy)]
        bestd = 10**9
        best = None
        for x, y in pool:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd or (d == bestd and (y, x) < (best[1], best[0])):
                bestd = d
                best = (x, y)
        goal = best

    gx, gy = goal
    base = abs(gx - ox) + abs(gy - oy)
    need_flip = 1 if len(unclaimed) < (w * h) // 4 else 0
    score_bias = (observation.get("self_territory_count", 0) - observation.get("opponent_territory_count", 0))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 1200 if need_flip else 700
        elif (nx, ny) in unclaimed:
            score += 70 if need_flip else 50

        if (nx, ny) in self_t:
            score += 15
        else:
            score -= 4

        d_goal = abs(nx - gx) + abs(ny - gy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_goal0 = abs(sx - gx) + abs(sy - gy)

        # Make progress to goal and increase distance from opponent slightly when behind.
        score += (d_goal0 - d_goal) * 6
        score += (d_opp - (abs(sx - ox) + abs(sy - oy))) * (2 if score_bias >= 0 else -1)

        # Prefer reducing opponent advantage by targeting closer to their territory/leader region.
        score += (base - (abs(nx - ox) + abs(ny - oy))) * 0.8

        # Avoid moving into squares that are adjacent to many obstacles (deterministic safety).
        adj_obs = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                adj_obs += 1
        score -= adj_obs * 2

        if score > best_score or (score == best_score and (dy, dx) < (best_move[1], best_move[0])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]