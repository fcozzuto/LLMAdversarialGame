def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs_set.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obs_set.add((int(p["x"]), int(p["y"])))

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res_list.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                res_list.append((int(r["x"]), int(r["y"])))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # If standing on a resource (or would collect), stop.
    if any((rx == sx and ry == sy) for (rx, ry) in res_list):
        return [0, 0]

    # Choose target by (opp_distance - self_distance) to exploit tempo,
    # with self distance as a secondary cost. Prefer nearer self when tempo is similar.
    best = None
    best_sc = -10**9
    for (rx, ry) in res_list:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Tempo advantage term; denier tends to mirror pursuit, so create selection pressure for being earlier.
        sc = (od - sd) * 3 - sd
        # Slight bias toward not too far goals late in the game.
        tr = int(observation.get("turns_remaining") or 0)
        if tr < 20:
            sc -= sd
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Move one step toward target, but avoid stepping into an obstacle if possible.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = []
    cand.append((dx, dy))
    # Alternative axis-prioritized moves if diagonal is blocked.
    cand.append((dx, 0))
    cand.append((0, dy))
    # Small "swerve" options (deterministic ordering).
    cand.append((dx, -dy if dy != 0 else 0))
    cand.append((-dx if dx != 0 else 0, dy))
    cand.append((0, 0))

    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            return [int(mx), int(my)]

    return [0, 0]