def choose_move(observation):
    w = int(observation.get("grid_width") or 0)
    h = int(observation.get("grid_height") or 0)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    s_terr = set(map(tuple, observation.get("self_territory") or []))
    o_terr = set(map(tuple, observation.get("opponent_territory") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        tx, ty = min(resources, key=lambda p: md(p[0], p[1], sx, sy))
    else:
        tx, ty = (w // 2, h // 2)

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            v = -10**14
        else:
            dres = md(nx, ny, tx, ty)
            dopp = md(nx, ny, ox, oy)
            v = -dres * 50 + dopp * 5
            if (nx, ny) in s_terr:
                v += 20
            if (nx, ny) in o_terr:
                v -= 120
        if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
            best = (v, dx, dy)
    return [int(best[1]), int(best[2])]