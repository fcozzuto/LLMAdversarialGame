def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    # Pick a target resource:
    # - Prefer ones we are strictly closer to (or at least not worse).
    # - If none, go for a resource that is closest to opponent to reduce their advantage.
    best = None
    for r in resources:
        rx, ry = r
        if not inside(rx, ry):
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # bigger is better for us
        score = (-adv, myd, rx, ry)  # minimize negative adv => maximize adv
        if best is None or score < best[0]:
            best = (score, rx, ry, adv)
    if best and best[3] >= 0:
        tx, ty = best[1], best[2]
    else:
        # Contest: choose resource that minimizes opponent lead (or maximizes our chance to be next)
        best2 = None
        for r in resources:
            rx, ry = r
            if not inside(rx, ry):
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd  # smaller is better
            score = (lead, myd, rx, ry)
            if best2 is None or score < best2[0]:
                best2 = (score, rx, ry)
        tx, ty = (best2[1], best2[2]) if best2 else (sx, sy)

    # If standing on target, prefer staying or move to keep opponent away (small tie-break).
    # Evaluate next move using one-step greedy with obstacle and opponent-aware tie-break.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd1 = cheb(nx, ny, tx, ty)
        opd1 = cheb(ox, oy, tx, ty)
        # Strongly prefer decreasing our distance to target,
        # and if equal, prefer increasing distance between opponent and target (slow them).
        # Also add small penalty for moving away from edges/center deterministically.
        val = (myd1, - (opd1 - myd1), nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]