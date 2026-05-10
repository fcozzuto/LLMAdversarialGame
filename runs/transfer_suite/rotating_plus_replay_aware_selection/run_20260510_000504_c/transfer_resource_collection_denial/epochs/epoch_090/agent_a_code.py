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

    if not res_list:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    # Pick a resource that we can arrive earlier than the opponent; otherwise minimize opponent advantage.
    best = None
    for rx, ry in res_list:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Higher is better: win margin first, then prefer nearer overall.
        key = (sd - od, sd)
        # We want smaller (sd-od)?? Actually if sd < od then sd-od negative => good.
        # Choose minimal key lexicographically.
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Evaluate moves: avoid obstacles/out-of-bounds, reduce distance to target, and keep away from opponent if contested.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        contested = cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty) <= 0
        # Deterministic scoring
        val = nd * 10 + (1 if contested else 0) * (0 if opd > 1 else 5) + (0 if (nx, ny) == (tx, ty) else 1)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves blocked, stay.
    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]