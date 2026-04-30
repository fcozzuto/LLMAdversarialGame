def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick best target deterministically: maximize how far ahead we are vs opponent.
    if resources:
        best_t = None
        best_lead = None
        best_me = None
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - md  # positive => we are closer/equal-first
            if best_t is None or lead > best_lead or (lead == best_lead and (best_me is None or md < best_me)) or (lead == best_lead and md == best_me and (rx, ry) < best_t):
                best_t = (rx, ry)
                best_lead = lead
                best_me = md
        tx, ty = best_t
    else:
        # No resources visible: drift toward center-ish (deterministic).
        tx, ty = w // 2, h // 2

    # One-step evaluation: prefer reducing our distance to target and (slightly) increasing opponent distance to same target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Strongly reduce our distance; lightly discourage moves that bring opponent target closer (via lead).
        val = -myd * 100 - (opd - myd) * 2
        # If target tie, prefer moving in lexicographically smaller direction for determinism.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]