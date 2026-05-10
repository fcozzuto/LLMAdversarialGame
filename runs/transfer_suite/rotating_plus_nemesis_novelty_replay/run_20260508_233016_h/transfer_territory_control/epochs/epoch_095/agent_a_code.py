def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not (0 <= x < w and 0 <= y < h): 
            continue
        if (x, y) in obstacles:
            continue

        score = 0
        if (x, y) in oppT:
            score += 200
        elif (x, y) in unclaimed:
            score += 120
        elif (x, y) in selfT:
            score += 40
        else:
            score += 10

        d_opp = abs(x - ox) + abs(y - oy)
        d_opp_now = abs(sx - ox) + abs(sy - oy)
        score += (d_opp_now - d_opp) * 25

        score += -abs(x - (ox)) * 1 + -abs(y - (oy)) * 0  # tiny tie-breaker

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]