def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (-(do - ds), ds, rx, ry)  # maximize (do-ds), then closer to self
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            dtarget = cheb(nx, ny, tx, ty)
            datt = cheb(ox, oy, tx, ty)  # tie-break: prefer moves that improve our lead
            do_self = cheb(nx, ny, ox, oy)
            key = (dtarget, -((datt - cheb(nx, ny, tx, ty)) if resources else 0), do_self, dx, dy)
        else:
            dopp = cheb(nx, ny, ox, oy)
            key = (-dopp, cheb(nx, ny, tx, ty), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]