def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    best_move = (0, 0)
    if self_is_evader:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            mob = mobility(nx, ny)
            corner_bias = -(min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
            center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            key = (dist2, mob, corner_bias, -center_pen, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
    else:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            mob = mobility(nx, ny)
            center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            key = (-dist2, mob, -center_pen, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]