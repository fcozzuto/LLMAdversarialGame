def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

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

    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]

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

    dist_s = bfs_dist(sx, sy)
    dist_o = bfs_dist(ox, oy)

    def best_margin_from(pos):
        px, py = pos
        best = -10**18
        for rx, ry in res:
            ds = dist_s.get((px, py))  # not usable here; keep separate
        return best

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Precompute BFS from candidate positions (<=9), keep deterministic and fast
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            candidates.append((nx, ny))
        else:
            candidates.append((sx, sy))
    # Deduplicate while preserving deterministic order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)

    center = (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18

    for nx, ny in uniq:
        dist_n = bfs_dist(nx, ny)
        val = 0