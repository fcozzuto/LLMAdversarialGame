def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def bfs(px, py):
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

    self_dist = bfs(sx, sy)
    opp_dist = bfs(ox, oy)

    reachable = []
    for r in resources:
        if r is not None and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if (tx, ty) in self_dist:
                sd = self_dist[(tx, ty)]
                od = opp_dist.get((tx, ty), 10**9)
                # Race advantage: large positive if opponent farther
                val = (od - sd) * 100 - sd
                reachable.append((val, sd, od, tx, ty))
    reachable.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))

    if reachable:
        _, _, _, tx, ty = reachable[0]
        d0 = self_dist.get((tx, ty), None)
        if d0 is None:
            return [0, 0]
        # pick deterministic neighbor that stays on a shortest path to target
        best = (10**9, 10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in self_dist and self_dist[(nx, ny)] == d0 - 1:
                score = (cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), abs(dx) + abs(dy))
                cand = (score[0], score[1], score[2], dx, dy)
                if cand < best:
                    best = cand
        if best[3] != 0 or best[4] != 0:
            return [best[3], best[4]]
        # If already adjacent in a way that fails, fall back to greedy safe step toward target
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    # No reachable resources: move to maximize distance from opponent and avoid obstacles
    best = None
    for dx, dy in dirs