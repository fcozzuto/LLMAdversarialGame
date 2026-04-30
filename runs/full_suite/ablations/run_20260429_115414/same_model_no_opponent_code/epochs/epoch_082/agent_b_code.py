def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if not res:
        # drift toward center if no resources
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = -1 if sx > cx else (1 if sx < cx else 0)
        dy = -1 if sy > cy else (1 if sy < cy else 0)
        return [dx, dy]

    # Choose target with best advantage: minimize (self_dist - opp_dist)
    best = None
    for x, y in res:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # prefer taking resources we can reach earlier; break ties toward closer-to-self
        score = (sd - od, sd, x, y)
        if best is None or score < best[0]:
            best = (score, x, y)
    _, tx, ty = best

    # Move one step toward target while maximizing same advantage at next position
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = sd - od
            # small tie-breaker: prefer moving closer to the target
            dist = sd
            # and prefer not staying if equally good
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            candidates.append((adv, dist, stay_pen, nx, ny, dx, dy))
    candidates.sort()
    return [int(candidates[0][5]), int(candidates[0][6])] if candidates else [0, 0]