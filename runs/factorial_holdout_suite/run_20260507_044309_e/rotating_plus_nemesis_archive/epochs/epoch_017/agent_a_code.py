def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    res = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if res:
        best = None
        best_key = None
        for rx, ry in res:
            myd = man((sx, sy), (rx, ry))
            opd = man((ox, oy), (rx, ry))
            # Prefer resources where we are closer; prioritize winning margin, then closer
            key = (-(opd - myd), myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        best_move = [0, 0]
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            myd = man((nx, ny), (tx, ty))
            opd = man((ox, oy), (tx, ty))
            # Also slightly reduce chance opponent is closer after our move
            val = (opd - myd, -myd, -abs(nx - tx) - abs(ny - ty))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # No visible resources: move toward center, but avoid being approached
    cx, cy = w // 2, h // 2
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dcen = man((nx, ny), (cx, cy))
        do = man((nx, ny), (ox, oy))
        # If opponent is closer than us to center, prioritize kiting; else prioritize center
        opp_to_center = man((ox, oy), (cx, cy))
        my_to_center = man((sx, sy), (cx, cy))
        kite = 2 if opp_to_center < my_to_center else 1
        val = (-dcen, kite * do, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move