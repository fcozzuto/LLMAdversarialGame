def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    obs = set((x, y) for x, y in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer being able to reach first (or close), while deprioritizing those the opponent is near.
        # Add slight bias toward resources that are "down/right" in our quadrant to break ties deterministically.
        lead = do - ds
        tie = -((rx - 3.5) ** 2 + (ry - 3.5) ** 2) * 1e-4
        blk_pen = -200000 if (rx, ry) in obs else 0
        score = lead * 1000 - ds * 10 + tie + blk_pen
        key = (score, -ds, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    if (tx, ty) in obs:
        # fallback to nearest unblocked resource
        cand = []
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            cand.append((man(sx, sy, rx, ry), rx, ry))
        if not cand:
            return [0, 0]
        cand.sort(key=lambda t: (t[0], t[1], t[2]))
        _, tx, ty = cand[0]

    # Choose a legal move that greedily reduces distance to the target, with obstacle avoidance.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d = man(nx, ny, tx, ty)
        # Small deterministic tie-break: prefer diagonal when equally good, then lower dx, then lower dy.
        diag = 1 if dx != 0 and dy != 0 else 0
        key = (d, -diag, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]