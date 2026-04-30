def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_from(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obs:
            return None
        dist = {(x0, y0): 0}
        q = [(x0, y0)]
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

    self_dist = bfs_from((sx, sy))
    if not res:
        cx, cy = (w // 2, h // 2)
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = max(abs(nx - cx), abs(ny - cy))
                if d < best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    opp_dist = bfs_from((ox, oy))
    # Choose target with best advantage; prefer reachable and higher (opp-self) gap.
    best_target = None
    best_val = -10**18
    limit = res[:12]
    for tx, ty in limit:
        if self_dist is None or (tx, ty) not in self_dist:
            continue
        ss = self_dist[(tx, ty)]
        if opp_dist is not None and (tx, ty) in opp_dist:
            oo = opp_dist[(tx, ty)]
        else:
            oo = ss + 5  # treat as not easily reachable by opponent
        # prioritize taking ahead, then faster, then closer to center
        center_pen = max(abs(tx - w // 2), abs(ty - h // 2))
        val = (oo - ss) * 1000 - ss * 3 - center_pen
        if val > best_val:
            best_val = val
            best_target = (tx, ty)

    if best_target is None:
        # Fall back: move to any reachable resource based on self-only shortest distance
        best = (10**9, 0, 0)
        for dx,