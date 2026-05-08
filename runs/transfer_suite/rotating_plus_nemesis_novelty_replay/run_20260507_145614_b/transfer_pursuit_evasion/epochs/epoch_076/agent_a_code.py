def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Evader_corner behavior: head toward the corner that is farthest from us (harder to reach if we don't cut off).
    target = max(corners, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy)))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_val = None
    tx, ty = target

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        # Intercept/cutoff blend: reduce distance to evader, but also position toward its likely corner.
        v = 0.7 * dist2(nx, ny, ox, oy) + 0.3 * dist2(nx, ny, tx, ty)
        if best_val is None or v < best_val:
            best_val = v
            best = (dxm, dym)
        elif v == best_val:
            # Deterministic tiebreaker: prefer moves that reduce distance to opponent, then toward target corner.
            cur = dist2(nx, ny, ox, oy)
            best_dx, best_dy = best
            bx, by = sx + best_dx, sy + best_dy
            best_op = dist2(bx, by, ox, oy)
            if cur < best_op:
                best = (dxm, dym)
            elif cur == best_op and dist2(nx, ny, tx, ty) < dist2(bx, by, tx, ty):
                best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]