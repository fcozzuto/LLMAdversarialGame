def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        dso = man(sx, sy, ox, oy)
        best_t = None
        best_v = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent (tempo), while avoiding center tie weirdness.
            v = (do - ds) * 12 - ds * 1.2 + (dso - (man(rx, ry, cx, cy))) * 0.2
            if best_v is None or v > best_v or (v == best_v and (rx, ry) < best_t):
                best_v = v
                best_t = (rx, ry)

        tx, ty = best_t
        best_move = None
        best_mv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            ns = man(nx, ny, tx, ty)
            no = man(ox, oy, tx, ty)
            v = (no - ns) * 12 - ns * 1.2 - (man(nx, ny, cx, cy) * 0.05)
            # Small nudge to not stand still unless forced
            v -= 0.01 if dx == 0 and dy == 0 else 0.0
            if best_mv is None or v > best_mv or (v == best_mv and (nx, ny) < best_move):
                best_mv = v
                best_move = (nx, ny)
        if best_move is not None:
            return [best_move[0] - sx, best_move[1] - sy]

    # Fallback: move to maximize distance from opponent while drifting toward center.
    best_move = None
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = man(nx, ny, ox, oy) * 3 - man(nx, ny, cx, cy)
        v -= 0.01 if dx == 0 and dy == 0 else 0.0
        if best_v is None or v > best_v or (v == best_v and (nx, ny) < best_move):
            best_v = v
            best_move = (nx, ny)
    if best_move is None:
        return [0, 0]
    return [best_move[0] - sx, best_move[1] - sy]