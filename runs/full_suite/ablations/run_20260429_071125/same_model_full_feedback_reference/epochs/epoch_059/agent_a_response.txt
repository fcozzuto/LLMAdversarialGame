def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        opp_turn = cheb(ox, oy, ox, oy)  # deterministic no-op
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Evaluate best resource "swing" from this next cell: (opp_dist - self_dist)
            best_swing = -10**9
            best_dist = 10**9
            # Deterministic iteration order
            for rx, ry in sorted(resources):
                sdist = cheb(nx, ny, rx, ry)
                odist = cheb(ox, oy, rx, ry)
                swing = odist - sdist
                if swing > best_swing or (swing == best_swing and (sdist < best_dist or (sdist == best_dist and (rx < nx or ry < ny)))):
                    best_swing = swing
                    best_dist = sdist
            # Prefer higher swing; break ties by closeness to chosen resource and then by move order
            key = (best_swing, -best_dist)
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
        if best is not None:
            return [int(best[0]), int(best[1])]
    # No resources: drift to center while avoiding obstacles
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    tx = 0 if abs(sx - cx) < 0.5 else (1 if sx < cx else -1)
    ty = 0 if abs(sy - cy) < 0.5 else (1 if sy < cy else -1)
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            cand.append((dx, dy, cheb(nx, ny, int(cx), int(cy))))
    cand.sort(key=lambda t: (t[2], t[0], t[1]))
    return [int(cand[0][0]), int(cand[0][1])] if cand else [0, 0]