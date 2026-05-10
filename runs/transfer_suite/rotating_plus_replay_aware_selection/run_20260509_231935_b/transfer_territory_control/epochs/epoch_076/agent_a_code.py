def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    # Heuristic for target cells: prefer closer to us, farther from opponent, and slightly prefer edge control
    unclaimed = observation.get("unclaimed_cells") or []
    best_target = None
    best_val = None
    for p in unclaimed:
        if not (isinstance(p, (list, tuple)) and len(p) == 2):
            continue
        x, y = int(p[0]), int(p[1])
        if not legal(x, y):
            continue
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        edge = 1 if (x == 0 or y == 0 or x == w - 1 or y == h - 1) else 0
        # Higher is better
        val = (do - ds) * 3 + edge * 0.6 - (ds * 0.05)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (x, y)

    if best_target is None:
        # Fallback: go toward opponent position or our corner if unclaimed blocked
        best_target = (ox, oy)

    tx, ty = best_target
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, nx, ny)
        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        # Prefer stepping toward target while keeping distance advantage vs opponent
        score = -(ds2 * 1.3) + (do2 * 0.9) + edge * 0.4
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]