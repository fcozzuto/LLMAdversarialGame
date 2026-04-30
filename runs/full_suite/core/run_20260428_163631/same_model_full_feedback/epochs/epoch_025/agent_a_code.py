def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    cx, cy = w // 2, h // 2

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = None
    resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))

    for dx, dy, nx, ny in legal:
        if resources_sorted:
            # Relative advantage if we target the best remaining resource
            val = -10**9
            for rx, ry in resources_sorted:
                d_self = md(nx, ny, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                # Prefer being closer than opponent; also penalize moving farther from it
                rel = d_opp - d_self
                # Tie-break: slightly prefer higher y then x deterministically
                tie = -0.001 * (ry * w + rx)
                if rel + tie > val:
                    val = rel + tie
            # Mild preference to avoid giving opponent a closer route next to us
            threat = md(ox, oy, nx, ny)
            val += 0.01 * threat
        else:
            val = -md(nx, ny, cx, cy)  # head to center if no resources

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
        elif val == best_val:
            # deterministic tie-break: smallest dx, then dy
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]