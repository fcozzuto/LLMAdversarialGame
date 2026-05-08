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

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(x, y, T):
        cnt = 0
        if (x - 1, y) in T: cnt += 1
        if (x + 1, y) in T: cnt += 1
        if (x, y - 1) in T: cnt += 1
        if (x, y + 1) in T: cnt += 1
        return cnt

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        pos = (nx, ny)
        a_self = adj_count(nx, ny, selfT)
        a_opp = adj_count(nx, ny, oppT)

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_center = abs(nx - cx) + abs(ny - cy)

        if pos in selfT:
            v = -0.5 + 0.8 * a_self - 0.3 * a_opp - 0.01 * d_center
        elif pos in oppT:
            v = 6.0 + 2.0 * a_self - 1.2 * a_opp - 0.03 * d_center + 0.02 * d_to_opp
        elif pos in unclaimed:
            v = 4.0 + 2.4 * a_self - 1.0 * a_opp - 0.02 * d_center + 0.01 * d_to_opp
        else:
            v = 1.0 - 0.5 * a_opp - 0.02 * d_center

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]