def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, x, y):
        return abs(x - a) + abs(y - b)

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    if not resources:
        # Drift toward center while avoiding obstacles (deterministic fallback)
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = abs(nx - cx) + abs(ny - cy)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Pick a resource where we can arrive earlier; otherwise pick one that least helps the opponent.
    best_target = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        dself = man(sx, sy, tx, ty)
        dopp = man(ox, oy, tx, ty)
        # Prefer strictly earlier; if not, minimize how much worse we are.
        key = (-(1 if dself < dopp else 0), dself - dopp, dself, dopp, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target
    preferred = step_toward(tx, ty)

    # Choose move among legal ones that most reduces distance to the target; tie-break by keeping away from opponent.
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        # Slightly favor moves that match preferred direction and maintain lead.
        lead_now = (man(nx, ny, tx, ty) - man(ox, oy, tx, ty))
        match = 0 if (dx, dy) == preferred else 1
        val = (ds, match, lead_now, -do, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]