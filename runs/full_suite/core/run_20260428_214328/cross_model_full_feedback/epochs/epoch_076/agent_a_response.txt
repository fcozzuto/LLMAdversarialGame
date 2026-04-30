def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    me = (sx, sy)
    them = (ox, oy)

    if resources:
        best = None
        best_key = None
        for r in resources:
            myd = cheb(me, r)
            opd = cheb(them, r)
            lead = opd - myd  # positive: we're closer than opponent
            key = (lead, -myd, -r[0], -r[1])  # deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best = r

        tx, ty = best
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd = cheb((nx, ny), (tx, ty))
            opd = cheb(them, (tx, ty))
            # Encourage grabbing target sooner than opponent; slightly prefer reducing myd
            val = (myd + 0.35 * opd, -cheb((nx, ny), them), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward center, but keep away from obstacles-opponent contact
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb((nx, ny), (cx, cy))
        od = cheb(them, (nx, ny))
        val = (myd, -od, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]