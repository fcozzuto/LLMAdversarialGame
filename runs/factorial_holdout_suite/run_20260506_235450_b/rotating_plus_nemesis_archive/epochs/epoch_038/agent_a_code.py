def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = None

    # Heuristic: pick move that maximizes chance of being first to some resource,
    # while discouraging moves that give opponent an advantage to any nearby resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Strongly favor being closer; also favor reducing distance for near resources.
            gap = opd - myd
            if gap > 0:
                v += 220 + gap * 35 - myd * 3
            else:
                v += gap * 90 - myd * 1.5
            # Extra: avoid letting opponent already be adjacent while we aren't.
            if opd <= 1 and myd > opd:
                v -= 1200
        # Small tie-break: prefer staying mobile toward closest resource centroid.
        # (Deterministic, no randomness.)
        closest = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
        cx, cy = closest[0], closest[1]
        v -= man(nx, ny, cx, cy) * 0.6

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]