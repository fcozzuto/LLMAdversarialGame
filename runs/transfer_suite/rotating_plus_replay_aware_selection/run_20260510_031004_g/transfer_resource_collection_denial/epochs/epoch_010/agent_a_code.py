def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    res = [(int(p[0]), int(p[1])) for p in resources]
    scored = []
    for tx, ty in res:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer targets I can reach strictly earlier; otherwise minimize myd while keeping opd high.
        can_win = 1 if myd <= opd - 1 else 0
        score = can_win * 10_000 + (opd - myd) * 100 - myd
        scored.append((score, opd, -myd, -(tx + ty), (tx, ty)))
    scored.sort(reverse=True)
    tx, ty = scored[0][4]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Move to improve my approach, but also keep separation in distance advantage.
        adv = opd2 - myd2
        # If my move doesn't improve much, break ties by increasing distance to opponent.
        my2 = cheb(nx, ny, ox, oy)
        k = (-(myd2), -can_win if False else 0, -myd2, -opd2, -myd2 + adv, my2, 0, dx, dy)
        # Use a custom deterministic comparator without relying on missing variables.
        # Build final key: prioritize smaller myd2, then larger adv, then farther from opponent, then lexicographic delta.
        k = (myd2, -adv, -my2, dx, dy)
        if best is None or k < best[0]:
            best = (k, [dx, dy])

    return best[1]