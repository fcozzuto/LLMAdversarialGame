def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    target = None
    if res:
        bestd = None
        for rx, ry in res:
            d = cheb(sx, sy, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx < target[0] or (rx == target[0] and ry < target[1]))):
                bestd = d
                target = (rx, ry)

    if target is None:
        tx = -1 if ox > sx else (1 if ox < sx else 0)
        ty = -1 if oy > sy else (1 if oy < sy else 0)
        pref = []
        for dx, dy in moves:
            pref.append((-(abs((sx+dx)-ox)+abs((sy+dy)-oy)), dx, dy))
        pref.sort(key=lambda t: (t[0], t[1], t[2]))
        for _, dx, dy in pref:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        d_self = cheb(nx, ny, target[0], target[1])
        d_opp = cheb(ox, oy, target[0], target[1])
        score = -d_self
        if d_self == 0:
            score += 1000
        if cheb(nx, ny, ox, oy) <= 1 and (d_self < d_opp):
            score += 5
        candidates.append((score, d_self, dx, dy))
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    if candidates:
        _, _, dx, dy = candidates[0]
        return [int(dx), int(dy)]
    return [0, 0]