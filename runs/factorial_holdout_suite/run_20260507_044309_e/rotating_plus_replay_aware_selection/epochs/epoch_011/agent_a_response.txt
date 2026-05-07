def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Prefer breaking sweep_rows by aiming for a different row than opponent when possible
    def row_bias(ry):
        if ry == oy: return -1.5
        return 0.0

    # Pick best target deterministically from current state
    def best_target_from(px, py):
        best = None
        best_sc = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer/equal
            central = -cheb(px, py, cx, cy) * 0.05
            parity_break = row_bias(ry)
            # If close to target, prioritize it
            near = 1.2 if ds <= 1 else 0.0
            sc = adv * 3.0 + central + parity_break + near
            if best_sc is None or sc > best_sc or (sc == best_sc and (ds < best[0])):
                best_sc = sc
                best = (rx, ry, ds, do)
        return best

    # Simulate one step for each move, then score by resulting advantage vs predicted opponent greedy step
    target = best_target_from(sx, sy)
    if target is None:
        return [0, 0]
    tx, ty, _, _ = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)

        # Opponent greedy one-step toward (tx,ty)
        stepx = 0 if tx == ox else (1 if tx > ox else -1)
        stepy = 0 if ty == oy else (1 if ty > oy else -1)
        nxo, nyo = ox + stepx, oy + stepy
        if not inb(nxo, nyo):
            # if blocked, stay (deterministic)
            nxo, nyo = ox, oy
        do2 = cheb(nxo, nyo, tx, ty)

        # Score: maximize immediate advantage over opponent after their step, plus small centrality
        adv_now = do - ds
        adv_after = do2 - ds
        central = -cheb(nx, ny, cx, cy) * 0.03
        # Encourage collecting resources quickly (more weight when opponent is close)
        quick = 1.0 if ds <= 1 else 0.0
        # If we're on opponent's row and we can take a different row resource, prefer that
        rb = row_bias(ty)

        score = adv_after * 4.0 + adv_now * 0.6 + central + quick + rb
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]