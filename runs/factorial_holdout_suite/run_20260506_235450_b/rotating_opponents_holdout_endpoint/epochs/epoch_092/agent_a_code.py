def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def cell_key(tx, ty):
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer resources that are hard for opponent to reach and easy for us.
        # Add small bias if we are aligned with opponent in row/col (contesting lines).
        contest = 0
        if ty == oy:
            contest += 2
        if tx == ox:
            contest += 1
        return (sd - od + contest * 2, sd, -tx, -ty)

    best = None
    bestt = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        k = cell_key(tx, ty)
        if best is None or k < best:
            best, bestt = k, (tx, ty)

    # If no resource (or all blocked), move away from opponent if possible; else stay.
    if bestt is None:
        candidates = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obs:
                    continue
                candidates.append((man(nx, ny, ox, oy), -man(nx, ny, sx, sy), dx, dy))
        if not candidates:
            return [0, 0]
        candidates.sort(reverse=True)
        return [int(candidates[0][2]), int(candidates[0][3])]

    tx, ty = bestt

    # Choose move that maximizes improvement toward target while keeping safe.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d0 = man(sx, sy, tx, ty)
            d1 = man(nx, ny, tx, ty)
            # Prefer reducing distance to target; break ties by denying opponent proximity.
            den = -man(nx, ny, ox, oy)
            # Small penalty for moving away.
            improv = d0 - d1
            moves.append((improv, den, -abs((nx - tx)) - abs((ny - ty)), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][3]), int(moves[0][4])]