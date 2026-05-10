def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_dist = abs(sx - ox) + abs(sy - oy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0

        if (nx, ny) in opp_t:
            score += 320
        elif (nx, ny) in unclaimed:
            score += 70
        elif (nx, ny) in self_t:
            score += 12

        dx_c = nx - cx
        dy_c = ny - cy
        score += 60 - int((dx_c * dx_c + dy_c * dy_c) ** 0.5 * 10)

        nd_opp = abs(nx - ox) + abs(ny - oy)
        score += (opp_dist - nd_opp) * 3
        if (nx, ny) in self_t:
            score += 6
        if (nx, ny) in opp_t:
            score += 10 - min(10, nd_opp)

        score += (1 if (nx, ny) == (ox, oy) else 0)

        if score > best_score:
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]