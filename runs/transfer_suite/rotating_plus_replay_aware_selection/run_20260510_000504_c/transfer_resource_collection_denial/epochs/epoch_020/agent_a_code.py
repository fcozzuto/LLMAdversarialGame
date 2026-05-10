def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                res.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))
    res = [p for p in res if p not in obstacles]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_step(tx, ty, prefer=False):
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_self = md(nx, ny, tx, ty)
            # avoid giving opponent an edge: penalize increasing their distance to the same target
            d_opp = md(ox, oy, tx, ty)
            # choose lexicographically by self distance, then (optionally) by how much we improve the contest
            score = (d_self, 0) if not prefer else (d_self, md(ox, oy, tx, ty) - d_opp)
            if best is None or score < best[0]:
                best = (score, [dx, dy])
        return best[1] if best else [0, 0]

    if not res:
        tx, ty = w // 2, h // 2
        return best_step(tx, ty)

    my_candidates = []
    opp_closest = None
    opp_best_d = None
    for (rx, ry) in res:
        d_my = md(sx, sy, rx, ry)
        d_op = md(ox, oy, rx, ry)
        if d_my <= d_op:
            my_candidates.append((d_my, d_op, rx, ry))
        if opp_best_d is None or d_op < opp_best_d:
            opp_best_d = d_op
            opp_closest = (rx, ry)

    if my_candidates:
        my_candidates.sort()
        _, _, tx, ty = my_candidates[0]
        return best_step(tx, ty)
    else:
        # Deny: go toward the resource opponent is closest to, but do not overshoot.
        rx, ry = opp_closest
        mx, my = (sx + ox) // 2, (sy + oy) // 2
        # target a point along the line to reduce their capture rate
        tx, ty = (rx + mx) // 2, (ry + my) // 2
        return best_step(tx, ty)