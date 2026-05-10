def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = p[0], p[1]
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    cells = []
    for p in observation.get("unclaimed_cells") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            cells.append((x, y))

    if not cells:
        for p in observation.get("resources") or []:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                cells.append((x, y))

    target = None
    if cells:
        cells = cells[:80]
        best = None
        for x, y in cells:
            d1 = man(x, y, sx, sy)
            d2 = man(x, y, ox, oy)
            val = (d1, -d2, x, y)
            if best is None or val < best:
                best = val
                target = (x, y)

    if target is None:
        tx, ty = (W // 2), (H // 2)
    else:
        tx, ty = target

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_mv = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        val = (d_to_t, -d_to_o, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_mv = (dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]