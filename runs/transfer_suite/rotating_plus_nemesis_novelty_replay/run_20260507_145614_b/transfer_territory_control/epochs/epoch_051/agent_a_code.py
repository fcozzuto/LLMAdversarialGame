def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))
    myt = observation.get("self_territory") or []
    myset = set((int(p[0]), int(p[1])) for p in myt if p and len(p) >= 2)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Frontier expansion: aim for unclaimed cells adjacent to our territory.
    frontier = []
    if myset:
        for (x, y) in myset:
            for dx, dy in dirs:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                    frontier.append((nx, ny))

    candidates = list(set(frontier)) if frontier else list(unclaimed)

    if not candidates:
        # Fallback: head to a deterministic center bias point.
        tx, ty = (w // 2, h // 2)
    else:
        # If we are ahead, prioritize nearby expansion; if behind, prioritize cells closer to us than opponent.
        ahead = float(observation.get("self_territory_count", 0)) >= float(observation.get("opponent_territory_count", 0))
        best = None
        best_key = None
        for (x, y) in candidates:
            d1 = dist((sx, sy), (x, y))
            d2 = dist((ox, oy), (x, y))
            # Deterministic tie-breakers using coordinates.
            key = (d1, 0 if ahead else d2, x, y) if ahead else (d1 - d2, d1, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        tx, ty = best

    # Choose one step that minimizes distance to target (avoid obstacles when possible).
    best_move = (0, 0)
    best_md = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        md = dist((nx, ny), (tx, ty))
        key = (md, abs(dx)+abs(dy), dx, dy)
        if best_md is None or key < best_md:
            best_md = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]