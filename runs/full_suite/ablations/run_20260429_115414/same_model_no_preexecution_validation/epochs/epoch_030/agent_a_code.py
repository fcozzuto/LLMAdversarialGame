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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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

    valid_res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                if (x, y) in self_dist and (x, y) in opp_dist:
                    valid_res.append((x, y))

    target = None
    best = None
    for x, y in valid_res:
        ds = self_dist[(x, y)]
        do = opp_dist[(x, y)]
        advantage = do - ds  # positive means we arrive earlier
        # Tie-breakers: prefer smaller ds, then lexicographic for determinism
        key = (-advantage, ds, x, y)
        if best is None or key < best:
            best = key
            target = (x, y)

    if target is None:
        # fallback: head to center-ish or just stay
        tx, ty = (w // 2, h // 2)
        best_step = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                v = abs(nx - tx) + abs(ny - ty)
                if best_val is None or v < best_val or (v == best_val and (dx, dy) < best_step):
                    best_val = v
                    best_step = (dx, dy)
        return [best_step[0], best_step[1]]

    tx, ty = target
    curd = self_dist[(sx, sy)]
    best_step = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs and (nx, ny) in self_dist:
            if self_dist[(nx, ny)] <= curd:
                # Prefer the step that decreases distance to target along shortest path; tie-break lexicographically
                v = self_dist[(nx, ny)]
                if best_val is None or v < best_val or (v == best_val and (dx, dy) < best_step):
                    best_val = v
                    best_step = (dx, dy)

    # If none reduced distance (should be rare), pick step that minimizes distance to target by dist-to-target proxy
    if best_val is None:
        best_step = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and