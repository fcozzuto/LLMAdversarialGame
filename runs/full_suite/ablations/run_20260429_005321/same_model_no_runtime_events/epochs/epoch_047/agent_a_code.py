def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not inb(sx, sy):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cur_near = None
    if resources:
        cur_near = min(max(abs(sx - rx), abs(sy - ry)) for rx, ry in resources)

    best = None
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if resources:
            near = min(max(abs(nx - rx), abs(ny - ry)) for rx, ry in resources)
            dist_to_opp = max(abs(nx - ox), abs(ny - oy))
            cur_dist_to_opp = max(abs(sx - ox), abs(sy - oy))
            val = (cur_near - near) * 10 - max(0, cur_dist_to_opp - dist_to_opp) * 3
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = -(max(abs(nx - cx), abs(ny - cy))) - max(0, (max(abs(sx - ox), abs(sy - oy)) - max(abs(nx - ox), abs(ny - oy)))) * 2
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]