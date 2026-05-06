def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if (not inb(nx, ny)) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            dcen = dist(nx, ny, cx, cy)
            d2 = dist(nx, ny, ox, oy)
            key = (dcen, -d2, dx, dy)
            if key < best:
                best = key
        return [best[2], best[3]]

    best_key = None
    best_move = (0, 0)
    cx, cy = (w - 1) // 2, (h - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (not inb(nx, ny)) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        our_best_d1 = 10**9
        our_best_adv = -10**9
        for rx, ry in resources:
            d1 = dist(nx, ny, rx, ry)
            d2 = dist(ox, oy, rx, ry)
            adv = d2 - d1
            if adv > our_best_adv or (adv == our_best_adv and d1 < our_best_d1):
                our_best_adv = adv
                our_best_d1 = d1

        dcen = dist(nx, ny, cx, cy)
        # Primary: maximize advantage over opponent for the chosen resource.
        # Secondary: minimize our distance to that resource.
        # Tertiary: prefer staying more central (edge patrol pressure).
        # Quaternary: prefer not moving diagonally as a deterministic tie-breaker.
        move_metric = (nx != sx and ny != sy)
        key = (-our_best_adv, our_best_d1, dcen, move_metric, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]