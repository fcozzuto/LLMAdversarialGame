def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        bestv = -10**18
        bestm = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = dist(nx, ny, ox, oy)
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    rlist = [(r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2]
    if not rlist:
        return choose_move({"self_position": (sx, sy), "opponent_position": (ox, oy), "grid_width": w, "grid_height": h, "resources": [], "obstacles": obstacles})

    target = None
    bestd = 10**18
    for rx, ry in rlist:
        d = dist(sx, sy, rx, ry)
        if d < bestd:
            bestd, target = d, (rx, ry)

    tx, ty = target
    bestv = -10**18
    bestm = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        myd = dist(nx, ny, tx, ty)
        od = dist(ox, oy, tx, ty)
        v = (od - myd) * 10 - myd
        if (nx, ny) == (tx, ty):
            v += 10**9
        if v > bestv:
            bestv, bestm = v, (dx, dy)
    return [bestm[0], bestm[1]]