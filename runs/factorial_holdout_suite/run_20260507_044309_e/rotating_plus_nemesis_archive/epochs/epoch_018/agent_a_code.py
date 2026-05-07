def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    if not resources:
        return [0, 0]

    # Target: maximize our lead (opponent_dist - self_dist), then minimize our distance, then deterministic tie by coordinates
    best = None
    best_key = None
    for rx, ry in resources:
        myd = man((sx, sy), (rx, ry))
        opd = man((ox, oy), (rx, ry))
        lead = opd - myd
        key = (lead, -myd, rx, ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    # Prefer moves that reduce our distance to target and improve lead; avoid obstacles
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd2 = man((nx, ny), (tx, ty))
        opd2 = man((ox, oy), (tx, ty))
        mkey = (opd2 - myd2, -myd2, -abs((tx - nx)) - abs((ty - ny)), dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]