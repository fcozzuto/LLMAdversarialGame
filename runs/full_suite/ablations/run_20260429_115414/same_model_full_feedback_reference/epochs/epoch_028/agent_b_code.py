def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        if inb(cx, cy):
            resources = [(cx, cy)]
        else:
            resources = [(0, 0)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose a high-value target: relatively closer than opponent.
    best_target = resources[0]
    best_val = None
    for i, (rx, ry) in enumerate(resources):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources where we can beat the opponent; tie-break deterministically.
        val = (od - sd) * 10 - sd
        if best_val is None or val > best_val or (val == best_val and i < resources.index(best_target)):
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic ordering shift by turn index to reduce repetition on ties.
    t = int(observation.get("turn_index", 0) or 0)
    shift = t % len(deltas)
    deltas = deltas[shift:] + deltas[:shift]

    best_move = [0, 0]
    best_move_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        nsd = man(nx, ny, rx, ry)
        nod = man(ox, oy, rx, ry)

        # Small obstacle proximity penalty (prefer more open moves deterministically).
        prox = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                tx, ty = nx + ex, ny + ey
                if (tx, ty) in obs:
                    prox += 1

        # If we reach target, prioritize immediately.
        reach = 40 if (nx == rx and ny == ry) else 0

        score = reach + (nod - nsd) * 10 - nsd - prox
        if best_move_score is None or score > best_move_score:
            best_move_score = score
            best_move = [dx, dy]

    return best_move