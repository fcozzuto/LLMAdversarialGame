def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            obs.add((p["x"], p["y"]))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2: return (p[0], p[1])
        if isinstance(p, dict) and "x" in p and "y" in p: return (p["x"], p["y"])
        return None
    targets = []
    for r in resources:
        rp = norm_pos(r)
        if rp is not None:
            targets.append(rp)
    target = None
    if targets:
        bestd = None
        for tx, ty in targets:
            d = cheb(sx, sy, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                target = (tx, ty)
    else:
        target = (ox, oy)
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_t = cheb(nx, ny, target[0], target[1])
        d_o = cheb(nx, ny, ox, oy)
        score = (d_t, -d_o, dx, dy)
        if best is None or score < best[0]:
            best = (score, (dx, dy))
    return list(best[1]) if best is not None else [0, 0]