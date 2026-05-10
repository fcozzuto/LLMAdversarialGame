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
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_score_for_pos(px, py):
        best = None
        for rx, ry in resources:
            ds = dist((px, py), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner; small tie-break favors lower raw ds
            s = (ds - do * 0.95, ds, rx, ry)
            if best is None or s < best:
                best = s
        return best[0] if best is not None else 0

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Evaluate move by resulting position's best target pressure.
        val = best_score_for_pos(nx, ny)
        # If equal, prefer moving closer to the currently best resource by our ds heuristic.
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val and (dx != 0 or dy != 0):
            best_move = [dx, dy]

    return best_move