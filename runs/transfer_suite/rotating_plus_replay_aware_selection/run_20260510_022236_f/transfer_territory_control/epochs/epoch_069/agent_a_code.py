def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    uc = set(unclaimed)

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    we_lead = (observation.get("self_territory_count", 0) >= observation.get("opponent_territory_count", 0))
    frontier = []
    for (x, y) in unclaimed:
        adj_op = any((nx, ny) in op_terr for nx, ny in neigh8(x, y))
        adj_me = any((nx, ny) in self_terr for nx, ny in neigh8(x, y))
        if adj_op and not adj_me:
            frontier.append((x, y))
    if not frontier:
        for (x, y) in unclaimed:
            adj_me = any((nx, ny) in self_terr for nx, ny in neigh8(x, y))
            if adj_me:
                frontier.append((x, y))
    if frontier:
        target = min(frontier, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        tx, ty = target
    elif op_terr:
        target = min(op_terr, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        tx, ty = target
    else:
        tx, ty = sx, sy

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # invalid move => stay; deterministic

        cell = (nx, ny)
        v = 0
        if cell in op_terr:
            v += 80  # strong: flipping opponent territory
        if cell in uc:
            v += 25  # expansion
        if cell in self_terr:
            v += 5   # consolidate
        if we_lead:
            # prioritize cutting off sweeps: move toward cells near opponent edge
            adj_op = any((px, py) in op_terr for px, py in neigh8(nx, ny))
            if adj_op and cell not in self_terr:
                v += 15
        # steer toward chosen target
        v += - (abs(tx - nx) + abs(ty - ny))

        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]