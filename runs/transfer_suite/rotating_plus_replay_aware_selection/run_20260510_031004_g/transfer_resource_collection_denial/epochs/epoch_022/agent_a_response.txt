def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]
    res = [(int(p[0]), int(p[1])) for p in resources]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def resource_score(px, py, rx, ry):
        myd = cheb(px, py, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where opponent is farther; also prefer closer to us
        return (opd - myd) * 20 - myd - (0 if (rx, ry) == (px, py) else 1)

    # Choose a target resource deterministically
    best_rx, best_ry = res[0]
    best_val = None
    for rx, ry in res:
        v = resource_score(sx, sy, rx, ry)
        tie = (-cheb(sx, sy, rx, ry), (rx + 31 * ry) % 7)
        if best_val is None or (v, tie) > best_val:
            best_val = (v, tie)
            best_rx, best_ry = rx, ry

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Greedy 1-step toward target, with slight repulsion from opponent-closest threats
    best_move = (0, 0)
    best_cmp = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dcur = cheb(nx, ny, best_rx, best_ry)
        # If we can pick up immediately, prioritize hard
        pick = 100000 if (nx, ny) == (best_rx, best_ry) else 0
        # Discourage moving into squares where opponent is much closer to some resource
        risk = 0
        # Check at most first 4 resources for speed/brevity
        for i in range(4 if len(res) >= 4 else len(res)):
            rx, ry = res[i]
            if (nx, ny) == (rx, ry):
                continue
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If opponent is very close compared to us, increase risk
            if od < md - 1:
                risk += (md - od)
        # Also prefer moves that don't increase distance to opponent too much (avoid giving free tempo)
        oppd = cheb(nx, ny, ox, oy)
        cmp = (pick - 100 * dcur - 5 * risk - 0.01 * oppd, -dcur, dx, dy)
        if best_cmp is None or cmp > best_cmp:
            best_cmp = cmp
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]