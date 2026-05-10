def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    their_terr = observation.get("opponent_territory") or []
    their_set = set((int(x), int(y)) for x, y in their_terr if x is not None and y is not None)

    adj_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    candidates = []

    # Prefer unclaimed cells that are adjacent to opponent territory (territory_counterclaim archetype).
    for x, y in their_set:
        for dx, dy in adj_dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in un_set:
                candidates.append((nx, ny))

    targets = candidates if candidates else (list(un_set) if un_set else [])

    # If no unclaimed exists, try to pressure opponent by stepping toward their territory.
    if not targets:
        if their_set:
            tx, ty = min(their_set, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        else:
            return [0, 0]
    else:
        t = observation.get("turn_index", 0) or 0
        parity = int(t) & 1
        # Alternate between L1 distance and "avoid adjacency to obstacles" proxy for determinism.
        def score(p):
            px, py = p
            base = abs(px - sx) + abs(py - sy)
            if parity:
                # Slight preference for cells closer to being adjacent to opponent territory
                adj = 0
                for ax, ay in adj_dirs:
                    if (px + ax, py + ay) in their_set:
                        adj += 1
                return (base, -adj, px, py)
            # Prefer targets that reduce max(dx,dy)
            return (max(abs(px - sx), abs(py - sy)), base, px, py)
        tx, ty = min(targets, key=score)

    # Choose best legal step toward (tx, ty), tie-broken deterministically by dir order and parity.
    dirs = [(0, 0)] + adj_dirs
    best = None
    t = observation.get("turn_index", 0) or 0
    p2 = int(t) & 7
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # If multiple, prefer steps that also increase adjacency to opponent territory.
        adj_gain = 0
        for ax, ay in adj_dirs:
            if (nx + ax, ny + ay) in their_set:
                adj_gain += 1
        key = (dist, -adj_gain, (i + p2) % len(dirs), nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]