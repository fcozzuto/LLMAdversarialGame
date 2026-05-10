def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Strongly maximize our reach advantage to any resource, with extra penalty if we are behind.
        v = -10**18
        for rx, ry in resources:
            my = man(nx, ny, rx, ry)
            opp = man(ox, oy, rx, ry)
            gap = opp - my
            if gap >= 0:
                score = 40 * gap - 2 * my
            else:
                # If opponent can grab earlier, avoid unless it's still the least-bad option.
                score = -60 * (-gap) - 2 * my
            # Prefer moves that reduce our distance more (helps when ties on gap).
            if score > v:
                v = score

        # Mild tie-break toward moving off current cell if all else equal.
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]