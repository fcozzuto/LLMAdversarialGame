def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            x = p.get("x", None)
            y = p.get("y", None)
            if x is not None and y is not None:
                obs.add((int(x), int(y)))
            else:
                q = p.get("position", None)
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    obs.add((int(q[0]), int(q[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            x = r.get("x", None)
            y = r.get("y", None)
            if x is not None and y is not None:
                res.append((int(x), int(y)))
            else:
                q = r.get("position", None)
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    res.append((int(q[0]), int(q[1])))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        best_cell = None
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; also slight tie-break for closeness.
            sc = (od - sd, -sd)
            if best_cell is None or sc > best_cell:
                best_cell = sc

        # If we can't improve, still choose deterministically smallest dx/dy ordering.
        if best is None:
            best = (best_cell, dx, dy)
        else:
            if best_cell > best[0]:
                best = (best_cell, dx, dy)
            elif best_cell == best[0]:
                if (dx, dy) < (best[1], best[2]):
                    best = (best_cell, dx, dy)

    return [int(best[1]), int(best[2])]