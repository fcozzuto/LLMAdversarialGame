def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    target = None
    if resources:
        best_key = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            key = (d_me, -d_op, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)

    if target is None:
        moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    rx, ry = target
    preferred = []
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, rx, ry)
        d_op = cheb(ox + (1 if ox < rx else -1 if ox > rx else 0), oy + (1 if oy < ry else -1 if oy > ry else 0), rx, ry)
        # primary: get closer to target; secondary: keep opponent far from target; tertiary: deterministic tie-break
        key = (d_me, -d_op, rx - nx, ry - ny, dx, dy)
        preferred.append((key, dx, dy))
    preferred.sort(key=lambda t: t[0])
    return [preferred[0][1], preferred[0][2]] if preferred else [0, 0]