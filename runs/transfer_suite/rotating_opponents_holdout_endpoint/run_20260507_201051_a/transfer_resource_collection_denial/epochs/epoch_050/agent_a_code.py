def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = rx - sx
    dy = ry - sy
    if dx > 0:
        mdx = 1
    elif dx < 0:
        mdx = -1
    else:
        mdx = 0
    if dy > 0:
        mdy = 1
    elif dy < 0:
        mdy = -1
    else:
        mdy = 0

    nx, ny = sx + mdx, sy + mdy
    if (mdx != 0 or mdy != 0) and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [mdx, mdy]

    cands = []
    if mdx != 0:
        cands.append([mdx, 0])
    if mdy != 0:
        cands.append([0, mdy])
    if mdx != 0 and mdy != 0:
        cands.append([mdx, mdy])
    cands.append([0, 0])

    for cdx, cdy in cands:
        tx, ty = sx + cdx, sy + cdy
        if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
            return [int(cdx), int(cdy)]
    return [0, 0]