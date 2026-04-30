def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    if resources:
        cx, cy = sx, sy
        bestd = 10**18
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                cx, cy = x, y
        tx, ty = cx, cy
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        val = -dist
        if resources:
            if (nx, ny) == (tx, ty):
                val += 1000000
        if val > best[2]:
            best = (dx, dy, val)
    if best[2] == -10**18:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            if inside(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]