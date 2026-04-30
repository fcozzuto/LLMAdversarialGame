def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    opp_d = cheb(sx, sy, ox, oy)
    res_list = resources
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dres = 10**9
        onres = False
        for rx, ry in res_list:
            d = cheb(nx, ny, rx, ry)
            if d < dres:
                dres = d
            if nx == rx and ny == ry:
                onres = True
        if dres == 10**9:
            dres = 0
        dp = cheb(nx, ny, ox, oy)
        s = 0
        if res_list:
            s += 50 if onres else 0
            s += -dres
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            s += -abs(nx - cx) - abs(ny - cy)
        s += -30 if dp <= 1 else 0
        if opp_d <= 2 and dp < opp_d:
            s -= 5
        if best is None or s > best_score:
            best_score = s
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best