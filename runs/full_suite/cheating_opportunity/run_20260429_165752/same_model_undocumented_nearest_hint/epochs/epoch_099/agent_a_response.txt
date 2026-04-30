def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [W - 1, H - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    # Choose target resource: nearest by Chebyshev with deterministic tie-break.
    if resources:
        tx, ty = resources[0]
        bestd = cheb(sx, sy, tx, ty)
        for x, y in resources[1:]:
            d = cheb(sx, sy, x, y)
            if d < bestd or (d == bestd and (x, y) < (tx, ty)):
                bestd = d
                tx, ty = x, y
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestscore = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Greedy progress to target plus repulsion from opponent to avoid contested cells.
        dist_to = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        # Slight preference for staying closer to opponent early when scores are tied: dampen repulsion when far.
        rep = (dist_opp <= 2) * (50 - 25 * dist_opp) + (dist_opp > 2) * (-(dist_opp // 2))
        # Stronger reward for collecting target immediately.
        collect = 200 if (nx, ny) == (tx, ty) else 0
        score = collect - 10 * dist_to + rep

        if best is None or score > bestscore or (score == bestscore and (dx, dy) < best):
            bestscore = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]