def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(t) for t in (observation.get("self_territory") or []))
    oppT = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(x, y, T):
        cnt = 0
        if (x - 1, y) in T: cnt += 1
        if (x + 1, y) in T: cnt += 1
        if (x, y - 1) in T: cnt += 1
        if (x, y + 1) in T: cnt += 1
        return cnt

    best_move = (0, 0)
    bestv = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in selfT:
            base = 0.0
        elif (nx, ny) in oppT:
            base = 2.3
        elif (nx, ny) in unclaimed:
            base = 1.3
        else:
            base = 0.4

        our_adj = adj_count(nx, ny, selfT)
        opp_adj = adj_count(nx, ny, oppT)

        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        toward_pen = 0.0
        if (nx, ny) not in oppT and dist_to_opp <= 2:
            toward_pen = 0.9 * (3 - dist_to_opp)  # avoid getting chased unless capturing

        center_bias = -0.02 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))

        val = base + 0.28 * our_adj - 0.18 * opp_adj + center_bias - toward_pen

        if val > bestv:
            bestv = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]