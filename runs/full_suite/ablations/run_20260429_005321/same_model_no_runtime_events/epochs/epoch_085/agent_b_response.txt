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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose target resource where opponent is relatively less competitive.
    bestR = None
    bestScore = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer closer to me; avoid if opponent is much closer.
        score = (opd - myd) * 2 - myd
        if score > bestScore:
            bestScore = score
            bestR = (rx, ry)

    # If no resources, drift away from opponent while respecting obstacles toward center.
    if bestR is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = bestR

    bestMove = [0, 0]
    bestVal = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Main: reduce distance to target.
        distT = cheb(nx, ny, tx, ty)
        # Secondary: if can prevent opponent by occupying/approaching their nearest target, slight bias.
        distO = cheb(nx, ny, ox, oy)
        # Soft obstacle/edge safety: prefer moves that stay away from obstacles neighbors.
        neighPenalty = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1)]:
            px, py = nx + ax, ny + ay
            if not (0 <= px < w and 0 <= py < h):
                neighPenalty += 1
            elif (px, py) in obstacles:
                neighPenalty += 2
        val = (-3 * distT) + (0.4 * distO) - (0.3 * neighPenalty)
        # Small deterministic tie-breaker: prefer moves with lower (dx^2+dy^2) to reduce jitter.
        val -= (dx*dx + dy*dy) * 0.01
        if val > bestVal:
            bestVal = val
            bestMove = [dx, dy]

    return bestMove