def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = observation.get("grid_width", 1)
    gh = observation.get("grid_height", 1)

    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)

    res = observation.get("resources", []) or []
    resources = [(p[0], p[1]) for p in res if isinstance(p, (list, tuple)) and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for dx, dy, nx, ny in moves:
            my_best = (-10**9, 10**9, 10**9)  # (gain, -myd, oppd)
            for rx, ry in resources:
                myd = man(nx, ny, rx, ry)
                oppd = man(ox, oy, rx, ry)
                gain = oppd - myd
                key = (gain, -myd, oppd, rx, ry)
                if my_best[0] < key[0] or (my_best[0] == key[0] and (my_best[1], my_best[2]) > (-key[1], key[2])):
                    my_best = (gain, -myd, oppd)
            final_key = (my_best[0], my_best[1], -my_best[2], -abs(nx - ox) - abs(ny - oy), dx, dy)
            if best_key is None or final_key > best_key:
                best_key = final_key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best = None
    best_key = None
    for dx, dy, nx, ny in moves:
        d = man(nx, ny, ox, oy)
        key = (-d, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]