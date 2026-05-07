def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 0)]

    if not resources:
        dx = 0
        if ox > sx:
            dx = 1
        elif ox < sx:
            dx = -1
        dy = 0
        if oy > sy:
            dy = 1
        elif oy < sy:
            dy = -1
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mdx, mdy in moves[:-1]:
            nx, ny = sx + mdx, sy + mdy
            if valid(nx, ny):
                return [mdx, mdy]
        return [0, 0]

    target = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, target[0], target[1])
        opp_d = cheb(nx, ny, ox, oy)
        score = (d, -opp_d, dx, dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    if best is not None:
        return best[1]
    return [0, 0]