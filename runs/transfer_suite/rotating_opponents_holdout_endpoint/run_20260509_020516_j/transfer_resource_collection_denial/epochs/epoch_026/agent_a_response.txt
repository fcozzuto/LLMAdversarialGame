def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", None) or []
    obstacles = set()
    for p in (observation.get("obstacles", None) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start, limit=6):
        if (start[0], start[1]) in obstacles: return {}
        dist = {(start[0], start[1]): 0}
        q = [(start[0], start[1])]
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

    ds = bfs((sx, sy), 6)
    do = bfs((ox, oy), 6)

    def step_toward(target):
        tx, ty = target
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return step_toward((cx, cy))

    # Estimate which resources opponent is likely to grab first; prefer resources where we're not behind.
    best_score = -10**18
    best_res = resources[0]
    for rx, ry in resources:
        sd = ds.get((rx, ry), 10**6)
        od = do.get((rx, ry), 10**6)
        # Higher is better: be earlier than opponent; also prefer closer absolute.
        score = (od - sd) * 1000 - sd
        # Deterministic tie-break
        score = score - (rx * 11 + ry)
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    return step_toward(best_res)