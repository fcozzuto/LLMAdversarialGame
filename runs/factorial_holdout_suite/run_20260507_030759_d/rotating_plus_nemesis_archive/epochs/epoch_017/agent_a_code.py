def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    resources = []
    for p in res:
        try:
            resources.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a target resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        key = (do - ds, -ds, -do, tx, ty)
        if best is None or key > best_key:
            best = (tx, ty)
            best_key = key
    tx, ty = best

    # Score candidate moves by: (opponent distance advantage) + progress to target.
    # Also avoid stepping into obstacles; if all blocked, fall back to best scoring without obstacle check.
    def eval_move(dx, dy, check_obst):
        nx, ny = sx + dx, sy + dy
        if check_obst and (nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst):
            return None
        ns = md(nx, ny, tx, ty)
        no = md(ox, oy, tx, ty)
        # Prefer grabbing (landing on resource), then maximizing advantage and progress.
        grab = 1 if (nx, ny) == (tx, ty) else 0
        return (grab, no - ns, -ns, -md(nx, ny, ox, oy), dx, dy)

    best_move = None
    best_val = None

    # First try with obstacle/bounds filtering.
    for dx, dy in moves:
        v = eval_move(dx, dy, True)
        if v is None:
            continue
        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]

    # If blocked (should be rare), try without obstacle/bounds check (engine will keep in place).
    if best_move is None:
        for dx, dy in moves:
            v = eval_move(dx, dy, False)
            if best_val is None or v > best_val:
                best_val = v
                best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]