def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turn = int(observation.get("turn_index", 0) or 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target resource deterministically.
    remain = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    phase = (turn + remain) % 3
    best = None
    best_key = None
    for x, y in resources:
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        # Main: win contention (target where opponent is relatively worse).
        # Phase tweak: late game or odd phase slightly favors blocking closer lanes.
        contention = (do - ds) * 1200
        self_push = -ds * (10 if phase == 0 else (6 if phase == 1 else 4))
        opp_push = do * (2 if phase == 0 else 1)
        # Mild center preference to stabilize paths.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -(abs(x - cx) + abs(y - cy)) * (2 if phase != 2 else 4)
        score = contention + self_push + opp_push + center
        key = (-score, x, y)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    # Choose the next step toward target, while staying away from opponent.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_target = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Encourage reducing distance to target and increasing distance to opponent.
        val = (-d_target * 100) + (d_opp * 3)
        # Deterministic micro-adjustment to avoid oscillation.
        if (dx == 0 and dy == 0) and remain > 0:
            val -= 5
        key = (-val, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]