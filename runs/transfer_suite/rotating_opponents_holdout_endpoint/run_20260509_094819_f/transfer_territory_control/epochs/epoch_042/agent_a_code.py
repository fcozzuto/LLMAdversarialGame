def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    cx, cy = w // 2, h // 2
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    # Prefer stepping into unclaimed adjacent to our territory (frontier expansion).
    frontier = []
    for (x, y) in uncla:
        if man(x, y, sx, sy) > 5:
            continue
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            if (x + ax, y + ay) in selfT:
                frontier.append((x, y))
                break

    # If no local frontier, move toward an unclaimed cell that is central and reachable-ish.
    if frontier:
        tx, ty = min(frontier, key=lambda p: (man(sx, sy, p[0], p[1]), man(p[0], p[1], cx, cy), p[1], p[0]))
    else:
        if uncla:
            tx, ty = min(uncla, key=lambda p: (man(sx, sy, p[0], p[1]) + 2 * man(p[0], p[1], cx, cy), p[1], p[0]))
        else:
            tx, ty = cx, cy

    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        v = 0
        if cell in uncla: v += 30
        if cell in selfT: v += 5
        if cell in oppT: v += 14 - man(nx, ny, sx, sy) * 0.3
        # Keep pressure toward target; slight preference for center.
        v += -man(nx, ny, tx, ty)
        v += -0.15 * man(nx, ny, cx, cy)
        # Avoid running straight into opponent if we can.
        if man(nx, ny, observation.get("opponent_position", [w-1, h-1])[0], observation.get("opponent_position", [w-1, h-1])[1]) <= 1:
            v -= 6 if cell not in oppT else 0
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best