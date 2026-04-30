def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_resource_dist(x, y):
        md = None
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if md is None or d < md:
                md = d
        return 10**9 if md is None else md

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            d = best_resource_dist(nx, ny)
            # Prefer smaller distance to nearest resource; slightly prefer moving away from opponent
            score = (-d, abs(nx - ox) + abs(ny - oy))
        else:
            # No resources: move toward center, avoid opponent
            score = (-(abs(nx - cx) + abs(ny - cy)), abs(nx - ox) + abs(ny - oy))
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]