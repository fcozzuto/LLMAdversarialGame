def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    bestv = -10**9
    for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dres = cheb(nx, ny, ox, oy)
        dov = cheb(nx, ny, ox, oy)
        # Prefer getting closer to resources; avoid opponent adjacency; slight preference to stay away from walls via staying safe.
        v = -dres * 10 + dov * 2
        # Penalize stepping next to obstacles (roughness)
        adj = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1)]:
            tx, ty = nx + ax, ny + ay
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                adj += 1
        v -= adj
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]
    return best if best is not None else [0, 0]