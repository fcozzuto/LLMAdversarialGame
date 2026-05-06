def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = None
    # Strategy: secure a resource we can reach first; otherwise deny by heading to a resource far in time from opponent
    # and keep y away from opponent to counter "sweep_rows"-like pressure.
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        y_gap = abs(ry - oy)
        # Primary: time advantage; Secondary: prefer larger y_gap to avoid row-sweeps.
        if ds < do:
            sc = (do - ds) * 1000 + y_gap * 10 - ds
        else:
            sc = (do - ds) * 1000 + y_gap * 10 - do  # maximize disadvantage to opponent
        if best is None or sc > best_score:
            best = (rx, ry)
            best_score = sc

    tx, ty = best

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # If opponent likely sweeping our row, add penalty for moves that reduce y-separation.
        y_sep = abs(ny - oy)
        penalty = 0
        if abs(ny - oy) <= 1:
            penalty = -y_sep
        val = d + penalty
        if best_d is None or val < best_d:
            best_d = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]