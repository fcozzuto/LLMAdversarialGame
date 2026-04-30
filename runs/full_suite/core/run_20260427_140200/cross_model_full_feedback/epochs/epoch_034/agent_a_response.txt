def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def target_value(nx, ny, rx, ry):
        d_me = man(nx, ny, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # Prefer getting closer while making the resource worse for opponent.
        return (d_opp - d_me) * 3 - d_me

    best = None
    best_dxdy = [0, 0]

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Choose the best resource to pursue from this candidate move.
            v = None
            for rx, ry in resources:
                tv = target_value(nx, ny, rx, ry)
                if v is None or tv > v:
                    v = tv
            # Break ties by prefer smaller distance to nearest resource.
            if v is None:
                continue
            if best is None or v > best:
                best = v
                best_dxdy = [dx, dy]
            elif v == best:
                cur_best_dist = min(man(sx + best_dxdy[0], sy + best_dxdy[1], r[0], r[1]) for r in resources)
                cand_dist = min(man(nx, ny, r[0], r[1]) for r in resources)
                if cand_dist < cur_best_dist:
                    best_dxdy = [dx, dy]
    else:
        # No resources: move toward center while keeping deterministic avoidance of obstacles.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, cx, cy)
            v = -d
            if best is None or v > best:
                best = v
                best_dxdy = [dx, dy]

    dx, dy = best_dxdy[0], best_dxdy[1]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    nx, ny = sx + dx, sy + dy
    if not legal(nx, ny):
        return [0, 0]
    return [dx, dy]