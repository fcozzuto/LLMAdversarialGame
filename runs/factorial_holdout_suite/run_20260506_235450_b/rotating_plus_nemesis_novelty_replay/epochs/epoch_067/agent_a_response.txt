def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    res = []
    for r in resources:
        try:
            rx, ry = r
            if inb(rx, ry) and (rx, ry) not in obstacles:
                res.append((rx, ry))
        except:
            pass

    opp_dist = None
    if opp_exists:
        opp_dist = lambda rx, ry: abs(ox - rx) + abs(oy - ry)
    self_dist = lambda rx, ry: abs(sx - rx) + abs(sy - ry)

    best = None
    best_key = None
    if res:
        for rx, ry in res:
            sd = self_dist(rx, ry)
            od = opp_dist(rx, ry) if opp_exists else 0
            # Prefer resources we are closer to than opponent; then nearer.
            key = (-(od - sd), sd, rx, ry)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md = abs(nx - tx) + abs(ny - ty)
        score = 0
        if res and (nx, ny) in res:
            score += 10**7
        # Main objective: reduce distance to chosen target.
        score += -1000 * md
        # Secondary: maintain advantage against denier by reducing opponent's closeness.
        if opp_exists and res:
            best_adv = None
            for rx, ry in res:
                sd2 = abs(nx - rx) + abs(ny - ry)
                od2 = abs(ox - rx) + abs(oy - ry)
                adv = od2 - sd2
                if best_adv is None or adv > best_adv:
                    best_adv = adv
            score += best_adv
        candidates.append((score, md, dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    candidates.sort()
    return [candidates[0][2], candidates[0][3]]