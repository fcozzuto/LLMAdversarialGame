def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            unclaimed.append((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    best = 10**9
    for x, y in unclaimed:
        d = man(sx, sy, x, y)
        if d < best:
            best = d
            target = (x, y)
    if target is None and resources:
        best = 10**9
        for x, y in resources:
            d = man(sx, sy, x, y)
            if d < best:
                best = d
                target = (x, y)
    if target is None:
        target = (ox, oy)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
    tx, ty = target
    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            score = man(nx, ny, tx, ty)
            if score < best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move