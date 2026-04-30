def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w - 1, h - 1), (0, 0), (0, h - 1), (w - 1, 0)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Primary: nearest resource to self.
    tp = resources[0]
    bestp = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < bestp:
            bestp = d
            tp = (rx, ry)

    # Secondary: opponent's nearest resource; if it's much closer to opponent, contest it.
    to = resources[0]
    besto = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < besto:
            besto = d
            to = (rx, ry)

    contest = 0
    if besto + 1 < bestp:
        contest = 1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: fixed move order.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d1 = cheb(nx, ny, tp[0], tp[1])
        score = -d1
        if contest:
            d2 = cheb(nx, ny, to[0], to[1])
            # Prefer moves that get closer to opponent's target; also subtly avoid giving them easier access.
            score += -0.6 * d2
            score += 0.1 * cheb(ox, oy, tp[0], tp[1])  # keep pressure near primary target
        else:
            # When not contesting, still bias away from opponent's direct route to their nearest.
            d2 = cheb(nx, ny, to[0], to[1])
            score += -0.1 * d2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not (isinstance(dx, int) and isinstance(dy, int) and dx in (-1, 0, 1) and dy in (-1, 0, 1)):
        return [0, 0]
    return [dx, dy]