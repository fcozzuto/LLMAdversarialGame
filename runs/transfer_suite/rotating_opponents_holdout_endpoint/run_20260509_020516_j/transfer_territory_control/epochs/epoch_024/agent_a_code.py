def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            unclaimed.append((x, y))

    def man(x, y, a, b):
        d = x - a
        if d < 0: d = -d
        e = y - b
        if e < 0: e = -e
        return d + e

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    target = None
    if unclaimed:
        # Deterministic: sort by distance, then coordinates
        best = None
        for x, y in unclaimed[:60]:
            d = man(sx, sy, x, y)
            key = (d, x, y)
            if best is None or key < best[0]:
                best = (key, (x, y))
        if best:
            target = best[1]

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue
        if target is not None:
            key = (man(nx, ny, target[0], target[1]), man(nx, ny, ox, oy), dx, dy)
        else:
            # No unclaimed info: move toward center, but avoid staying still if possible
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            distc = abs(nx - cx) + abs(ny - cy)
            key = (distc, man(nx, ny, ox, oy), dx == 0 and dy == 0, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]