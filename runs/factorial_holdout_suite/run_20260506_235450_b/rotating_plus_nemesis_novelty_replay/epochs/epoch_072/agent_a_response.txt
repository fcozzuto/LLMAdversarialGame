def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    rx0 = sy0 = None
    if resources:
        for r in resources:
            if r[0] == sx and r[1] == sy:
                return [0, 0]

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -dist(nx, ny, cx, cy)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_key = (-10**18, 10**18, 0)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate how strongly this move positions us to be first on some visible resource.
        best_adv = -10**18
        best_selfd = 10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            if opp_exists:
                od = dist(ox, oy, rx, ry)
                adv = od - sd  # positive means we are closer than opponent
            else:
                adv = -sd
            if adv > best_adv or (adv == best_adv and sd < best_selfd):
                best_adv = adv
                best_selfd = sd
        # Prefer maximal advantage; then prefer shorter own distance; then deterministic tie-break.
        key = (best_adv, -best_selfd)
        if key > (best_key[0], best_key[1]):
            best_key = (best_adv, best_selfd, dx + 2 * dy)
            best_move = [dx, dy]

    return best_move