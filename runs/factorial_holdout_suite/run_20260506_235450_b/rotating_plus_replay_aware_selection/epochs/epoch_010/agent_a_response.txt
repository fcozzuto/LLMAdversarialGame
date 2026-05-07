def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            v = (man(nx, ny, ox, oy), man(nx, ny, sx, sy), ny, nx, dx, dy)
            if best is None or v < best[0]:
                best = (v, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    # Pick target resource where we are ahead (our_dist < opp_dist), else minimize opp advantage.
    best_target = None  # (priority, rx, ry)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        ahead = ds - do  # negative means we arrive sooner
        # Primary: arrive sooner (more negative ahead), Secondary: shorter our distance, tertiary: stable tie by coords
        priority = (ahead, ds, ry, rx)
        if best_target is None or priority < best_target[0]:
            best_target = (priority, rx, ry)
    _, tx, ty = best_target

    # Choose the move that most reduces our distance to chosen target, with tie-break favoring staying ahead of opponent.
    best = None  # (score, dx, dy)
    for dx, dy, nx, ny in legal:
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)  # opponent position unchanged this turn
        score = (ds2, do2 - ds2, ny, nx, dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]