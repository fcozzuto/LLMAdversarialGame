def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -man(nx, ny, w // 2, h // 2)
            key = (score, -man(nx, ny, ox, oy), dx, dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    best_delta = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_adv = -10**18
        best_selfd = 10**18
        best_oppd = -10**18
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Maximize advantage in getting there first; slight preference for shorter self distance.
            adv = od - sd
            if adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and od > best_oppd))):
                best_adv, best_selfd, best_oppd = adv, sd, od

        key = (best_adv, -best_selfd, best_oppd, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_delta = [dx, dy]

    return best_delta if best_delta is not None else [0, 0]