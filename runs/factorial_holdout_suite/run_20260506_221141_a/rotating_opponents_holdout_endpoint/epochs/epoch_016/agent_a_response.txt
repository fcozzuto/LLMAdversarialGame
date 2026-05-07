def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**18, 0, 0)  # (score, nx, ny)

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Target that we can reach sooner than opponent; also prefer closer to us.
            worst = -10**18
            for rx, ry in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                gain = do - ds  # positive means we deny (closer than opponent)
                # Slightly prefer grabbing (ds small) and ending near resource.
                val = gain * 1000 - ds
                if val > worst:
                    worst = val
            # If no denial possible, just minimize ds to nearest resource.
            nearest_ds = min(man(nx, ny, rx, ry) for rx, ry in resources)
            score = (-worst) * 1 - nearest_ds
            if score < best[0]:
                best = (score, nx, ny)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Move one step toward (tx, ty) with deterministic tie-break.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((man(nx, ny, tx, ty), abs(dx), abs(dy), dx, dy))
    candidates.sort()
    if not candidates:
        return [0, 0]
    return [int(candidates[0][3]), int(candidates[0][4])]