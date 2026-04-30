def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a contested target: prefer resources where we are closer relative to opponent.
    tx, ty = None, None
    if resources:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Lower is better
            key = (ds - 0.6 * do, ds, do, rx, ry)
            if best is None or key < best:
                best = key
                tx, ty = rx, ry

    # Greedy step toward target, with opponent distance pressure and obstacle-safe tie-breaking.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if tx is None:
            # No resources: just drift to center-ish and away from opponent
            score = -man(nx, ny, w // 2, h // 2) + 0.3 * man(nx, ny, ox, oy)
        else:
            cur_ds = man(sx, sy, tx, ty)
            nxt_ds = man(nx, ny, tx, ty)
            # prefer reducing our distance; also discourage moving into areas where opponent is closer to target
            cur_do = man(ox, oy, tx, ty)
            # opponent doesn't move this turn; but we can still act on "relative position pressure"
            rel = (nxt_ds - 0.6 * cur_do)
            score = (cur_ds - nxt_ds) * 2.0 - rel * 0.8 + 0.25 * man(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: prefer staying closer to target, then farther from opponent, then lexicographic dx,dy
            if tx is not None:
                if man(nx, ny, tx, ty) < man(sx + best_move[0], sy + best_move[1], tx, ty):
                    best_move = [dx, dy]
            if man(nx, ny, ox, oy) > man(sx + best_move[0], sy + best_move[1], ox, oy):
                best_move = [dx, dy]
            elif man(nx, ny, ox, oy) == man(sx + best_move[0], sy + best_move[1], ox, oy):
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]