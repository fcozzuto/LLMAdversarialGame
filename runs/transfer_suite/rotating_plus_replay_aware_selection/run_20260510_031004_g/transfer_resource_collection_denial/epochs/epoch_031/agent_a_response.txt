def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best_r = resources[0]
    best_key = None
    for i, (rx, ry) in enumerate(resources):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (-(od - sd), sd, i, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    if sx == rx and sy == ry:
        return [0, 0]

    dx = 0
    if rx > sx: dx = 1
    elif rx < sx: dx = -1
    dy = 0
    if ry > sy: dy = 1
    elif ry < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_dist = None
    for mdx, mdy in moves:
        tx, ty = sx + mdx, sy + mdy
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
            continue
        d = cheb(tx, ty, rx, ry)
        key = (d, abs(mdx) + abs(mdy), mdx, mdy)
        if best_dist is None or key < best_dist:
            best_dist = key
            best_move = (mdx, mdy)

    return [best_move[0], best_move[1]]