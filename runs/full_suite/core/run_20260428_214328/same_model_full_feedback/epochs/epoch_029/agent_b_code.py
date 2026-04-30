def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def risk(x, y):
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obstacles:
                    r += 3
        return r

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            ahead = 1 if d_self < d_op else 0
            # Prefer resources we can reach sooner; otherwise prefer farther disadvantage (to avoid mirroring).
            key = (-(ahead), d_self + (0 if ahead else 2), d_op - d_self, rx + 100 * ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = pick_target()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # If we have no target, drift toward center-ish to reduce corner traps deterministically.
    if target is None:
        target = (w // 2, h // 2)

    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Greedy after-move: maximize chance to get a "contested" target while minimizing obstacle risk.
        d_self = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        contested_penalty = 0 if d_self < d_op else 6
        # Also consider immediate next-best resource if target is blocked/too far.
        alt = 10**9
        for rx, ry in resources:
            alt = min(alt, cheb(nx, ny, rx, ry))
        score = (d_self, alt, contested_penalty + risk(nx, ny), (nx + 31 * ny))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]