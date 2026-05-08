def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    last = None
    if observation.get("self_path"):
        path = observation.get("self_path")
        if isinstance(path, list) and path:
            lastp = path[-1]
            if lastp and len(lastp) >= 2:
                last = (int(lastp[0]), int(lastp[1]))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    bestd = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if last is not None and (nx, ny) == last:
            penalty = 1
        else:
            penalty = 0
        d = abs(nx - ox) + abs(ny - oy) + penalty
        if d < bestd:
            bestd = d
            best = (dx, dy)
    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                best = (dx, dy)
                break
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]