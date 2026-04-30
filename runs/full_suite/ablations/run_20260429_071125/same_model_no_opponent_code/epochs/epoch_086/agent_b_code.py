def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    if (sx, sy) in resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    rem = observation.get("remaining_resource_count", None)
    rem = int(rem) if rem is not None else len(resources)

    best = None
    # Prefer resources where we are not behind; if behind, still pick the least-bad capture.
    for x, y in resources:
        myd = cheb(sx, sy, x, y)
        opd = cheb(ox, oy, x, y)
        lead = opd - myd  # positive means I'm closer (better)
        # As resources dwindle, prioritize pure closeness.
        tighten = 0.35 if rem > 6 else (0.15 if rem > 3 else 0.0)
        key = (-lead - tighten * (myd * 0.1), myd, opd, x, y)
        if best is None or key < best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    # Greedy step toward target, but avoid walking into an obstacle and avoid giving opponent advantage
    # by not unnecessarily increasing distance to the target while we are the closest.
    cur_my = cheb(sx, sy, tx, ty)
    cur_op = cheb(ox, oy, tx, ty)
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy):
            myd = cur_my
            opd = cur_op
        else:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
        # If I'm currently closer, strongly prefer moves that don't let opponent become closer.
        if cur_my < cur_op:
            allow = 1 if myd <= opd else 0
        else:
            allow = 0
        # Deterministic tie-breakers: reduce my distance, then reduce opponent distance to their nearest resource
        # approx by using distance to target only (cheap).
        score = (-allow, myd, opd - myd, abs(dx) + abs(dy), dx, dy, nx, ny)
        if bestm is None or score < bestm[0]:
            bestm = (score, (dx, dy))
    return [int(bestm[1][0]), int(bestm[1][1])]