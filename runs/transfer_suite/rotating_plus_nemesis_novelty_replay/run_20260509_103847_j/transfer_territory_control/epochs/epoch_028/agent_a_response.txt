def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dcen = abs(nx - cx) + abs(ny - cy)
        score = -0.2 * dcen

        if (nx, ny) in opT:
            score += 50.0
        elif (nx, ny) in unT:
            score += 12.0
        elif (nx, ny) in selfT:
            score += 2.0

        # Frontier pressure: move toward nearest opponent cell unless blocked.
        if opT:
            near_op = min(opT, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            score += -0.08 * (abs(near_op[0] - nx) + abs(near_op[1] - ny))
        # Unclaimed expansion when no opponent nearby.
        if unT:
            near_un = min(unT, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            score += 0.03 * (1.0 / (1 + abs(near_un[0] - nx) + abs(near_un[1] - ny)))

        if (score, dx, dy) > best:
            best = (score, dx, dy)

    if best[0] == -10**18:
        return [0, 0]
    return [int(best[1]), int(best[2])]