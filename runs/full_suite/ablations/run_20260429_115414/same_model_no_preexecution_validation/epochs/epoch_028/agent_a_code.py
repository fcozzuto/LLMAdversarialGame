def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs_dist(px, py):
        if not inb(px, py) or (px, py) in obs:
            return {}
        dist = {(px, py): 0}
        q = [(px, py)]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[(x, y)] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs_dist(sx, sy)
    opd = bfs_dist(ox, oy)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = -10**18
    for x, y in res:
        d1 = myd.get((x, y), INF)
        d2 = opd.get((x, y), INF)
        if d1 >= INF and d2 >= INF:
            continue
        # Prefer resources we can reach sooner than opponent
        score = (d2 - d1) - 0.15 * d1
        # If opponent is unreachable, strongly prefer
        if d2 >= INF: score += 1000
        # If we are far but still reachable, penalize
        if d1 >= INF: score -= 1000
        if score > best_score:
            best_score = score
            best = (x, y)

    # Fallback: go to any reachable resource
    if best is None:
        if myd:
            # pick closest by BFS then by cheb
            best = min(res, key=lambda p: (myd.get(p, INF), cheb(sx, sy, p[0], p[1]))) if res else (sx, sy)
        else:
            return [0, 0]

    tx, ty = best
    curd = cheb(sx, sy, tx, ty)

    # Choose legal move that minimizes BFS dist to target; tie-break by safety and closing
    best_move = (0, 0)
    best_key = (10**18, 10**18, 10**18, 10**18)  # mydist, -oppdist, closeness, move_order

    # Precompute target distances from current by BFS map if available
    target_dist = None
    if (tx, ty) in myd:
        mydist_to_target = myd[(