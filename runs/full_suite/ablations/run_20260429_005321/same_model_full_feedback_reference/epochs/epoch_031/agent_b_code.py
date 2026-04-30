def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        dx = 0
        if sx > ox:
            dx = -1
        elif sx < ox:
            dx = 1
        dy = 0
        if sy > oy:
            dy = -1
        elif sy < oy:
            dy = 1
        if (sx + dx, sy + dy) in obstacles or not (0 <= sx + dx < w and 0 <= sy + dy < h):
            if (sx, sy) not in obstacles:
                return [0, 0]
            for mdx, mdy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1),(0,0)]:
                nx, ny = sx + mdx, sy + mdy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [mdx, mdy]
        return [dx, dy]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        mind = 10**9
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if d < mind:
                mind = d
        od = abs(ox - nx) + abs(oy - ny)
        if best is None or (mind, -od, dx, dy) < best[0]:
            best = ((mind, -od, dx, dy), [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]