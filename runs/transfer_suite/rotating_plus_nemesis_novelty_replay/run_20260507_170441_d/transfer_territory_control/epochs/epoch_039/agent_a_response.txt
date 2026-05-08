def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        score = 0.0

        if (nx, ny) in opp_t:
            score += 1600.0
            score += 120.0 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in unclaimed:
            score += 900.0
        elif (nx, ny) in self_t:
            score += 150.0
        else:
            score += 10.0

        d_op = abs(nx - ox) + abs(ny - oy)
        score += 14.0 * d_op  # prefer moves that keep distance while expanding

        d_ctr = abs(nx - cx) + abs(ny - cy)
        score += 120.0 - 10.0 * d_ctr  # drift toward center

        # avoid walking into the immediate opponent neighborhood unless it captures
        if (nx, ny) not in opp_t and d_op <= 2:
            score -= 250.0

        # slight bias: reduce movement churn
        score -= 2.0 * (abs(dx) + abs(dy))

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]