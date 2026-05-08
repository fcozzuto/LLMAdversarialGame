def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx, dy) == (0, 0) or (inb(nx, ny) and (nx, ny) not in obs):
                if (dx, dy) != (0, 0) and not inb(nx, ny):
                    continue
                if (dx, dy) != (0, 0) and (nx, ny) in obs:
                    continue
                valid.append((dx, dy))
    if (0, 0) not in valid:
        valid.append((0, 0))

    if not resources:
        tx, ty = (w - 1 if ox < w // 2 else 0), (h - 1 if oy < h // 2 else 0)
        best = min(valid, key=lambda m: abs((sx + m[0]) - tx) + abs((sy + m[1]) - ty))
        return [best[0], best[1]]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer moves that reduce distance to resources where we have an advantage over opponent
    best_move = None
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # If moving into obstacle (shouldn't happen), treat as worst
        if (dx, dy) != (0, 0) and ((nx, ny) in obs or not inb(nx, ny)):
            val = -10**9
        else:
            val = -10**9
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Advantage: we want sd < od; also favor absolute closeness
                advantage = (od - sd)
                collected_bias = 8 if sd == 0 else 0
                # Slight tie-break toward corners (helps against sweep-row patterns)
                corner_bias = (rx in (0, w - 1)) + (ry in (0, h - 1))
                candidate = 3 * advantage - sd + collected_bias + 0.2 * corner_bias
                if candidate > val:
                    val = candidate
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]