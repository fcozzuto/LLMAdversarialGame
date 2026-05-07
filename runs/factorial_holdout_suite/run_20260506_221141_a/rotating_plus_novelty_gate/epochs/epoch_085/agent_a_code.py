def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def mhd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    tr = observation.get("turns_remaining", 0)
    horizon = 6 if tr and tr < 12 else 1000000000

    # If we're late, just take the closest. Otherwise, use win-chance heuristic.
    if tr and horizon != 1000000000:
        best = None
        best_d = 10**9
        for x, y in res:
            d = mhd(sx, sy, x, y)
            if d < best_d or (d == best_d and (best is None or (x, y) < best)):
                best_d = d
                best = (x, y)
        tx, ty = best
    else:
        best = None
        best_score = -10**30
        for x, y in res:
            sd = mhd(sx, sy, x, y)
            od = mhd(ox, oy, x, y)

            # Prefer arriving earlier; still allow negative gap if nothing winnable.
            gap = od - sd  # positive means we arrive no later than opp
            arrive_bonus = gap * 20
            # Reduce stalling and slight favor for nearer cells
            time_pen = sd
            # Mild curvature tie-breaker via distance to the line between starts (deterministic)
            midx = (sx + ox) // 2
            midy = (sy + oy) // 2
            curv = - (mhd(x, y, midx, midy) // 2)

            # If gap is negative, damp it so we don't freeze when all targets are contested against us.
            if gap < 0:
                score = arrive_bonus * 0.3 - time_pen + curv
            else:
                score = arrive_bonus - time_pen + curv

            # Deterministic tie-break: lexicographic on (x,y)
            if score > best_score or (score == best_score and (best is None or (x, y) < best)):
                best_score = score
                best = (x, y)
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If blocked cell would trap us (rare), try one axis alternative deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in blocked:
        if (sx + dx, sy) not in blocked:
            return [dx, 0]
        if (sx, sy + dy) not in blocked:
            return [0, dy]
        return [0, 0]
    return [dx, dy]