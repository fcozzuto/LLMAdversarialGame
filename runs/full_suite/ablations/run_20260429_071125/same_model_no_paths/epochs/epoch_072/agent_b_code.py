def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if not inb(sx, sy):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target that we can reach no slower than opponent; tie-break deterministically.
    if resources:
        best_t = None
        best_key = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer targets where we are closer or equal; then minimize our distance and lexicographic coords.
            key = (0 if ds <= do else 1, ds - do, ds, tx, ty)
            if best_key is None or key < best_key:
                best_key, best_t = key, (tx, ty)
        tx, ty = best_t
    else:
        # Fallback: move toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # One-step greedy: minimize our distance to target; secondary: avoid moving closer to opponent.
    best_score = None
    best_delta = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds1 = cheb(nx, ny, tx, ty)
        do1 = cheb(nx, ny, ox, oy)
        # Slightly reward staying away from opponent.
        score = (ds1, do1 * -1, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_delta = [dx, dy]

    # If all moves blocked, stay.
    return best_delta