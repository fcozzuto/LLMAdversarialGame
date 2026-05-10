def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", p)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacles:
            return None
        return nx, ny

    best = None
    for tx, ty in resources:
        myd = dist((sx, sy), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # Prefer resources we can reach earlier; break ties by closer and by myd (smaller).
        score = (myd - opd, myd, tx, ty)
        if best is None or score < best[0]:
            best = (score, (tx, ty))
    target = best[1]
    tx, ty = target

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            p = clamp_move(dx, dy)
            if p is None:
                continue
            nx, ny = p
            my_next_d = dist((nx, ny), target)
            op_d = dist((ox, oy), target)
            # Also discourage moves that give opponent a tighter lead.
            obj = (my_next_d - op_d * 0.15, my_next_d, dx, dy)
            moves.append((obj, [dx, dy]))

    # Allow staying if all moves blocked or staying is best.
    p0 = (sx, sy)
    stay_obj = (dist(p0, target) - dist((ox, oy), target) * 0.15, dist(p0, target), 0, 0)
    best_move = [0, 0]
    best_val = stay_obj
    for obj, mv in moves:
        if obj < best_val:
            best_val = obj
            best_move = mv
    return best_move