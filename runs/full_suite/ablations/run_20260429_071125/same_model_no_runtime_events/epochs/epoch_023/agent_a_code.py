def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if isinstance(r.get("pos"), (list, tuple)) and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif r.get("x") is not None and r.get("y") is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    if resources:
        for x, y in resources:
            if inside(x, y):
                d = cheb(sx, sy, x, y)
                if best is None or d < best[0]:
                    best = (d, x, y)
        if best is None:
            best = (0, sx, sy)
        tx, ty = best[1], best[2]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        # small deterministic adjustment to avoid blocked immediate diagonal
        for cand in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + cand[0], sy + cand[1]
            if inside(nx, ny):
                return [int(cand[0]), int(cand[1])]

    # fallback: move toward center, but prefer staying away from opponent when possible
    cx, cy = (w - 1) // 2, (h - 1) // 2
    step = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if inside(nx, ny):
                # score: closer to center, and if tie, farther from opponent
                score = cheb(nx, ny, cx, cy) * 1000 - cheb(nx, ny, ox, oy)
                step.append((score, mx, my))
    step.sort()
    if step:
        _, mx, my = step[0]
        return [int(mx), int(my)]
    return [0, 0]