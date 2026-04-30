def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    me = (sx, sy)
    opp = (ox, oy)

    # Pick target we can reasonably beat (opponent not much closer); else fall back to nearest.
    best = None
    for rx, ry in sorted(resources):
        r = (rx, ry)
        myd = king(me, r)
        opd = king(opp, r)
        val = (myd - 0.85 * opd, myd, rx, ry)
        if best is None or val < best[0]:
            best = (val, r)
    target = best[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd_next = king((nx, ny), target)
        oppd_next = king((ox, oy), target)
        # Greedy toward target; also prefer moves that keep opponent from arriving sooner.
        score = (myd_next - 0.4 * oppd_next, myd_next, king((nx, ny), opp), dx, dy)
        if bestm is None or score < bestm[0]:
            bestm = (score, (dx, dy))
    if bestm is None:
        return [0, 0]
    return [int(bestm[1][0]), int(bestm[1][1])]