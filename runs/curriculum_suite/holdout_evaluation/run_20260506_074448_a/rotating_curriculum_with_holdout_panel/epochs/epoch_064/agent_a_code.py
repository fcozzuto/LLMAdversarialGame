def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_key = None

    if resources:
        scored = []
        for r in resources:
            if not r:
                continue
            rx, ry = r
            dS = abs(sx - rx) + abs(sy - ry)
            dO = abs(ox - rx) + abs(oy - ry)
            # Prefer resources we can reach sooner; break ties by closeness to center
            scored.append((dS - dO, dS, abs(rx - cx) + abs(ry - cy), rx, ry))
        scored.sort()
        # Consider only top few to stay fast
        targets = scored[:3]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Evaluate against best target
            key = None
            for _, _, _, tx, ty in targets:
                dS = abs(nx - tx) + abs(ny - ty)
                dO = abs(ox - tx) + abs(oy - ty)
                # maximize advantage -> minimize (dS-dO)
                local = (dS - dO, dS, abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy))
                if key is None or local < key:
                    key = local
            if key is None:
                key = (10**9, 10**9, 10**9, 10**9)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # No resources: go to center while staying away from opponent
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        key = (-dist((nx, ny), (ox, oy)), abs(nx - cx) + abs(ny - cy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move if best_key is not None else [0, 0]