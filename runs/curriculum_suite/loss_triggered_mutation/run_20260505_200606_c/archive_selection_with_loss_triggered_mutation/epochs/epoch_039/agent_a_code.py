def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None
    best_val = -10**9

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            val = adv * 100 - myd
            # if opponent is substantially ahead, still consider as a contest by minimizing our distance
            if adv < -1:
                val += (-(opd - myd)) * 0.5
            if val > best_val:
                best_val = val
                best_target = (rx, ry)
        tx, ty = best_target

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        # Prefer increasing distance from opponent to reduce contest risk
        opd = md(nx, ny, ox, oy)
        # Prefer reducing distance to target; small bonus for staying closer to target while avoiding obstacles indirectly
        score = (-myd * 10) + (opd * 0.2)
        # slight preference for forward-ish movement toward target
        if tx > sx and dx == 0:
            score -= 0.01
        if tx < sx and dx == 0:
            score -= 0.01
        if ty > sy and dy == 0:
            score -= 0.01
        if ty < sy and dy == 0:
            score -= 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]