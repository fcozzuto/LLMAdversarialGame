def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources we can arrive no later than opponent; then minimize our distance; break ties deterministically.
            key = (0 if myd <= opd else 1, myd, rx, ry, cheb(ox, oy, rx, ry))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources visible: move toward opponent corner to deny space
        tx, ty = ox, oy

    # Evaluate immediate moves with a "win-now" bias: reduce distance to target and avoid allowing opponent closer gain.
    cur_opd = cheb(ox, oy, tx, ty)
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        # Assume opponent next can improve; estimate their best possible distance reduction this turn.
        # (Deterministic local bound, not a search.)
        best_opd = cur_opd
        for odx, ody in moves:
            px, py = ox + odx, oy + ody
            if valid(px, py):
                d = cheb(px, py, tx, ty)
                if d < best_opd:
                    best_opd = d
        # Score: primary minimize our distance; secondary maximize distance advantage over opponent; slight preference toward target direction.
        val = (myd, -(myd - best_opd), (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]