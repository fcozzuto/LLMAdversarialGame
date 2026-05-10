def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def dist(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    res = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))
    if not res:
        return [0, 0]

    low_left = observation.get("remaining_resource_count", len(res))
    if low_left <= 3:
        tx, ty = min(res, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        best = None
        for rx, ry in res:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # positive: we are closer than opponent
            if ry == oy and abs(rx - ox) <= 3:
                adv -= 1.5  # likely opponent sweeps that row
            if rx == ox and abs(ry - oy) <= 3:
                adv -= 0.8  # mild for column-alignment too
            cand = (adv, -sd, rx, ry)
            if best is None or cand > best:
                best = cand
        tx, ty = best[2], best[3]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        sd2 = dist(nx, ny, tx, ty)
        od2 = dist(ox, oy, tx, ty)
        val = (od2 - sd2) * 1000 - sd2
        if low_left > 3:
            # small bias to not drift away from the most dangerous alternatives
            for rx, ry in res[:]:
                if (rx, ry) == (tx, ty):
                    continue
                # quick compare using only y alignment
                if ry == ny:
                    val += 2
                    break
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move