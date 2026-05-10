def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obs.add((int(p["x"]), int(p["y"])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))

    if not res:
        return [0, 0]

    def man(a, b, c, d):
        da, db = abs(a - c), abs(b - d)
        return da + db

    best = None
    best_key = None
    for (rx, ry) in res:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        if (best is None) or (opp_d - self_d, -self_d, -rx, -ry) > best_key:
            best_key = (opp_d - self_d, -self_d, -rx, -ry)
            best = (rx, ry)

    tx, ty = best
    step_deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = None
    for dx, dy in step_deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        hit = 1 if (nx, ny) in obs else 0
        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        advantage = opp_d - self_d
        # Deterministic tie-breakers: prefer fewer obstacle hits, then smaller self distance, then favor dx/dy order.
        key = (-hit, advantage, -self_d, -dx, -dy)
        if (best_score is None) or key > best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move