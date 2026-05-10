def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    # If unclaimed empty (rare), fall back to opponent territory border
    if not unclaimed:
        for p in observation.get("opponent_territory") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    unclaimed.append((x, y))
        if not unclaimed:
            return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    best_val = -10**18
    # Deterministic scan: small grid; still keep concise
    for x, y in unclaimed:
        ds = abs(x - sx) + abs(y - sy)
        do = abs(x - ox) + abs(y - oy)
        dc = abs(x - cx) + abs(y - cy)
        # Prefer center-first, then cells closer than opponent (intercept), then closer to us.
        val = (-2.2 * dc) + (1.1 * (do - ds)) + (-0.35 * ds)
        if val > best_val:
            best_val = val
            best = (x, y)

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose step that most improves distance to target while not stepping into obstacles
    best_step = (0, 0)
    best_d = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if d < best_d:
            best_d = d
            best_step = (dx, dy)
        elif d == best_d:
            # Tie-break: prefer reducing Manhattan to opponent (can disrupt), then lexicographic
            nds = abs(tx - nx) + abs(ty - ny)
            if nds == best_d:
                if (dx, dy) < best_step:
                    best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]