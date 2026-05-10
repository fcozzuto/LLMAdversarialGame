def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", None) or []
    obstacles = set()
    for p in (observation.get("obstacles", None) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs(start, limit=7):
        sx0, sy0 = start
        if (sx0, sy0) in obstacles: return {}
        dist = {(sx0, sy0): 0}
        q = [(sx0, sy0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[(x, y)]
            if d >= limit: continue
            nd = d + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy), 7)
    do = bfs((ox, oy), 7)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                key = (-max(abs(cx - nx), abs(cy - ny)), -abs(nx - ox) - abs(ny - oy), nx, ny)
                if best is None or key > best[0]:
                    best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best = None
    for rx, ry in resources:
        r = (int(rx), int(ry))
        d1 = ds.get(r, 10**9)
        d2 = do.get(r, 10**9)
        if d1 >= 10**8 and d2 >= 10**8:
            continue
        # Prefer resources we can get strictly sooner; otherwise, deny by taking those opponent can’t reach soon.
        delta = d2 - d1
        key = (delta, -d1, -r[0], -r[1])
        if best is None or key > best[0]:
            best = (key, r, d1, d2)

    target = best[1] if best else (resources[0][0], resources[0][1])

    # Choose one-step move that greedily minimizes our distance to the chosen target (with obstacle safety).
    tx, ty = int(target[0]), int(target[1])
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            d = max(abs(tx - nx), abs(ty - ny))
            # Secondary: avoid stepping closer to opponent's position (helps contest).
            sopp = max(abs(ox - nx), abs(oy - ny))
            key = (-d, sopp, -nx, -ny)
            if bestm is None or key > bestm[0]:
                bestm = (key, dx, dy)
    return [bestm[1], bestm[2]] if bestm else [0, 0]