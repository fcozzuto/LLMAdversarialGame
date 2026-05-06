def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turn = int(observation.get("turn_index", 0))

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick target resource where we are at least as competitive as opponent (prefer strictly better).
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        lead = sd - od  # negative means we arrive sooner
        # Also slightly prefer keeping toward middle to avoid straight-line traps.
        midbias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        key = (lead, midbias, (rx + ry + turn) % 2, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    # Fallback: head toward opponent (forces pressure), otherwise nearest free corner-ish.
    if best is None:
        tx, ty = (w - 1 if turn % 2 == 0 else 0), (h - 1)
    else:
        _, tx, ty = best

    # If opponent can take the same target much sooner, switch to a different resource (deterministic second choice).
    if best is not None:
        rx, ry = best[1], best[2]
        if dist(ox, oy, rx, ry) + 1 < dist(sx, sy, rx, ry):
            alt = None
            for r in resources:
                ax, ay = int(r[0]), int(r[1])
                if (ax, ay) in obs:
                    continue
                if ax == rx and ay == ry:
                    continue
                sd = dist(sx, sy, ax, ay)
                od = dist(ox, oy, ax, ay)
                lead = sd - od
                midbias = abs(ax - (w - 1) / 2.0) + abs(ay - (h - 1) / 2.0)
                key = (lead, midbias, (ax + ay + turn) % 2, sd, ax, ay)
                if alt is None or key < alt[0]:
                    alt = (key, ax, ay)
            if alt is not None:
                tx, ty = alt[1], alt[2]

    # Choose move that reduces distance to target while avoiding obstacles; deterministic tie-breaks.
    want = dist(sx, sy, tx, ty)
    order = moves if (turn % 2 == 0) else list(reversed(moves))
    bestm = [0, 0]
    bestscore = None
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        # Prefer blocking: also reduce opponent distance to the target when close competition.
        od = dist(ox, oy, tx, ty)
        opd_new = dist(ox, oy, tx, ty)
        # slight deterministic use of current opponent position relative to target
        opblock = abs((ox - tx) + (oy - ty)) % 3
        score = (0 if nd < want else 1, nd, abs(nx - tx) + abs(ny - ty), opblock, (dx, dy))
        if bestscore is None or score < bestscore:
            bestscore = score
            bestm = [dx, dy]

    return [int(bestm[0]), int(bestm[1])]