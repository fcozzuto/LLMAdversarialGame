def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inb(sx, sy):
        return [0, 0]

    if not resources:
        # Deterministic: drift toward center while avoiding obstacles.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_m = [0, 0]
        best_v = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            v = cheb(nx, ny, cx, cy)
            if best_v is None or v < best_v:
                best_v, best_m = v, [dx, dy]
        return best_m

    # Target: maximize (opponent farther than us), then closer to self, then coords.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my = cheb(sx, sy, rx, ry)
        opp = cheb(ox, oy, rx, ry)
        adv = opp - my  # higher is better
        key = (-adv, my, rx, ry)  # minimize negative advantage => maximize advantage
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Move: choose step that improves distance to target and also preserves advantage if possible.
    best_m = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        my2 = cheb(nx, ny, tx, ty)
        opp2 = cheb(ox, oy, tx, ty)
        adv2 = opp2 - my2
        score = (-adv2, my2, dx, dy)  # minimize negative adv => maximize adv
        if best_score is None or score < best_score:
            best_score = score
            best_m = [dx, dy]

    # If all moves blocked (unlikely), stay still.
    return best_m