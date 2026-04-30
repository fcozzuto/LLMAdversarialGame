def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    # Pick target that maximizes advantage: my_dist - 0.9*opp_dist (lower is better)
    best_t = resources[0]
    best_v = 10**18
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        v = md - 0.9 * od
        if v < best_v:
            best_v = v
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose move that reduces distance to target, while discouraging moving toward opponent's nearer resources
    opp_best = None
    opp_best_d = 10**18
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < opp_best_d:
            opp_best_d = d
            opp_best = (rx, ry)
    ax, ay = opp_best if opp_best else (tx, ty)

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        myd0 = cheb(sx, sy, tx, ty)
        # Penalties: step that helps opponent contest (move closer to opponent's best target)
        oppd = cheb(nx, ny, ax, ay)
        oppd0 = cheb(sx, sy, ax, ay)
        score = myd * 10 + (oppd0 - oppd) * 3
        # Small deterministic bias to avoid oscillation: prefer moves that don't increase distance too much
        score += max(0, myd - myd0) * 2
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]