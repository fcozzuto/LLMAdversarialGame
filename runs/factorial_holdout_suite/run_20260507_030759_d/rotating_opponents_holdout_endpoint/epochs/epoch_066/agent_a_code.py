def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in blocked:
                valid_res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid_res:
        # fallback: move to increase distance from opponent while staying safe
        best = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            key = (manh(nx, ny, ox, oy), -manh(nx, ny, sx, sy))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Target selection: prioritize resources we can reach no later than opponent; otherwise closest.
    best_t = None
    best_key = None
    for tx, ty in valid_res:
        sd = manh(sx, sy, tx, ty)
        od = manh(ox, oy, tx, ty)
        # Make "we beat them" dominate, then race quality, then stable tie
        key = (1 if sd <= od else 0, -(sd - od), -sd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Step selection: minimize our distance to target, prefer safer squares, and avoid letting opponent cut closer.
    best = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = manh(nx, ny, tx, ty)
        nod = manh(nx, ny, ox, oy)
        # Prefer getting closer; if equal, prefer staying farther from opponent; then deterministic tie by position
        key = (-nd, nod, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]