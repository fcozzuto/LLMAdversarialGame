def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target resource that we can potentially beat the opponent to.
    best = None  # (adv, myd, opd, rx, ry)
    for (rx, ry) in resources:
        myd0 = cheb(sx, sy, rx, ry)
        opd0 = cheb(ox, oy, rx, ry)
        adv = opd0 - myd0
        cand = (adv, -myd0, opd0, int(rx), int(ry))
        if best is None or cand > best:
            best = cand
    adv, _, _, tx, ty = best

    # Take a step that maximizes immediate advantage for this target,
    # while also slightly preferring moves that keep adv from worsening.
    best_move = None  # (score, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd1 = cheb(nx, ny, tx, ty)
        opd1 = cheb(ox, oy, tx, ty)
        score = (opd1 - myd1) * 1000 - myd1
        # If still tied, prefer staying closer to the best overall resources.
        # Deterministic tie-break: smallest (nx,ny) with equal score.
        if best_move is None or score > best_move[0] or (score == best_move[0] and (nx, ny) < (best_move[1], best_move[2])):
            best_move = (score, nx, ny)

    _, nx, ny = best_move
    dx = nx - sx
    dy = ny - sy
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    return [int(dx), int(dy)]