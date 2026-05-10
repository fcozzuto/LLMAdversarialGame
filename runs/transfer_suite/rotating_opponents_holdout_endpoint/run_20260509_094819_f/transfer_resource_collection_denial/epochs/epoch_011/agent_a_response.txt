def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Choose a target resource we are (relatively) closer to than the opponent.
    best = None
    best_key = None
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        tx, ty = int(r[0]), int(r[1])
        if (tx, ty) in obst:
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Lower is better: (we are closer) -> ds-do smaller; then tie-break by ds, then coordinates.
        key = (ds - do, ds, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    if best is None:
        return [0, 0]
    tx, ty = best

    # Move to best immediate neighbor w.r.t. relative advantage to the same target.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)  # opponent assumed stationary for one-step decision
        # Also discourage stepping farther than necessary.
        step_cost = man(nx, ny, tx, ty) - man(sx, sy, tx, ty)
        key = (ns - no, ns, step_cost, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]