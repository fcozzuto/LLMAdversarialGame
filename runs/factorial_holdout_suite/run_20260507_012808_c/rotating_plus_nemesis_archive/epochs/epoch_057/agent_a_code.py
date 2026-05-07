def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))
    res = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                res.append((x, y))
    directions = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
    best = None
    best_score = -10**18
    for dx, dy in directions:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if res:
            dsr = 10**9
            for rx, ry in res:
                t = cheb(nx, ny, rx, ry)
                if t < dsr:
                    dsr = t
            dvo = cheb(nx, ny, ox, oy)
            score = -dsr*10 + dvo
        else:
            score = cheb(nx, ny, ox, oy)  # drift away if no resources known
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]