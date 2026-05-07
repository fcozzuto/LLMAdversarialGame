def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set(obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    rx, ry = resources[0]
    bd = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        d = cheb(sx, sy, x, y)
        if bd is None or d < bd:
            bd = d
            rx, ry = x, y

    tr, ty = resources[0]
    bo = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        d = cheb(ox, oy, x, y)
        if bo is None or d < bo:
            bo = d
            tr, ty = x, y

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_us = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, tr, ty)
        d_opp_to_resource = cheb(ox, oy, tr, ty)
        score = (d_us, d_opp_to_resource + 0.15 * d_opp)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]