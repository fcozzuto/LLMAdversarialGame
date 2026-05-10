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
    best = (999999, 0, 0)
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty) + (0.25 * (abs(nx - ox) + abs(ny - oy)))
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    def score_move(nx, ny):
        if (nx, ny) in obstacles or nx < 0 or nx >= w or ny < 0 or ny >= h:
            return 10**9
        mr = 10**9
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if d < mr:
                mr = d
        steal = abs(nx - ox) + abs(ny - oy)
        return mr + 0.15 * steal - (0.2 if (nx, ny) in resources else 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        s = score_move(nx, ny)
        if s < best[0]:
            best = (s, dx, dy)

    return [int(best[1]), int(best[2])]