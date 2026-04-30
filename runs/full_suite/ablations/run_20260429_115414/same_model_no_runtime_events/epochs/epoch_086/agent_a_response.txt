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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_moves():
        moves = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1), (0, 0), (0, 1),
                 (1, -1), (1, 0), (1, 1)]
        resm = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                resm.append((dx, dy))
        return resm

    cand_moves = clamp_moves()

    if not resources:
        # Fall back: move toward the far corner opposite us (deterministic).
        tx = 0 if sx > ox else w - 1
        ty = 0 if sy > oy else h - 1
        best = None
        for dx, dy in cand_moves:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    # Denial strategy: prefer resources the opponent is closer to (so we contest them),
    # then prefer resources where our distance is close to (or slightly better than) theirs.
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Primary: maximize opponent lead (od - sd); i.e., resources opponent is likely to take.
        # Secondary: minimize our distance; Tertiary lexicographic for determinism.
        lead = od - sd
        key = (-(lead), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Move selection: greedily reduce distance to target, but discourage stepping into squares
    # that make us easier for opponent to contest (by checking opponent's distance after move).
    best = None
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Evaluate: primarily minimize myd; then maximize myd - opd (prefer positions that keep us competitive)
        # and prefer moves that also reduce distance to opponent slightly (when safe).
        key = (myd, (myd - opd), abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [int(best[1][0]), int(best[1][1])] if best else [0, 0]