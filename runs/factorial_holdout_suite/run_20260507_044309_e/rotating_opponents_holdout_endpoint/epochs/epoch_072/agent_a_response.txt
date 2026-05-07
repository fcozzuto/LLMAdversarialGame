def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) == (sx, sy):
            return [0, 0]
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, ry * w + rx)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    if (sx, sy) == (tx, ty):
        return [0, 0]

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = cheb(nx, ny, tx, ty)
                man = abs(dx) + abs(dy)
                moves.append((dist, man, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort()
    _, _, dx, dy = moves[0]
    return [int(dx), int(dy)]