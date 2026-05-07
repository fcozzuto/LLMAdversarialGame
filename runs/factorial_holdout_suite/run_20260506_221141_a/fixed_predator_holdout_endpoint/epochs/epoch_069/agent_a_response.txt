def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Target a resource we can reach sooner (deny opponent), otherwise pick the best "still-possible" one.
    best = None
    best_key = None
    for rx, ry in resources:
        my = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        self_closer = opd - my  # want positive
        tie = -(abs(rx - sx) + abs(ry - sy))
        # small deterministic preference for corner-ish resources
        corner = -((rx - (w - 1)) ** 2 + (ry - (h - 1)) ** 2)
        key = (self_closer, tie, corner, -my, -opd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministically rank moves: avoid obstacles/out-of-bounds, go to target, and keep away from opponent.
    best_mv = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # If we can contest (opponent not closer), prioritize tighter control; otherwise prioritize survival/spacing.
        my_now = cheb(sx, sy, tx, ty)
        op_now = cheb(ox, oy, tx, ty)
        contest = 1 if op_now - my_now >= 0 else 0
        score = (
            contest * (d_to_t * -3 + d_to_o) + (1 - contest) * (-d_to_t + d_to_o * 0.7),
            -d_to_t,
            d_to_o,
            dx * 0 + dy * 0,  # keep deterministic tuple shape
            rx := nx, ry := ny
        )
        if best_score is None or score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]