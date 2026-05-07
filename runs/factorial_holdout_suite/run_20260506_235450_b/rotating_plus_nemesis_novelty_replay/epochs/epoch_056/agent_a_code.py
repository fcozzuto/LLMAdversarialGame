def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (None, None))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            x, y = p
            if isinstance(x, int) and isinstance(y, int):
                obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    respos = []
    for r in resources:
        try:
            rx, ry = r
            if inb(rx, ry) and (rx, ry) not in obstacles:
                respos.append((rx, ry))
        except:
            pass

    if not respos or w <= 0 or h <= 0:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in respos:
            ds = abs(sx - rx) + abs(sy - ry)
            do = 10**9
            if ox is not None and oy is not None:
                do = abs(ox - rx) + abs(oy - ry)
            # Prefer resources where we are closer than opponent; tie-break by parity and distance.
            parity = (ds + (sx + sy)) & 1
            score = (do - ds, -parity, -ds, rx, ry)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]

    def step_value(nx, ny):
        d = abs(nx - tx) + abs(ny - ty)
        if ox is None or oy is None:
            return (-d, 0)
        # Slightly avoid stepping too close to opponent.
        adv = abs(ox - nx) + abs(oy - ny)
        return (-d, adv)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = step_value(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]