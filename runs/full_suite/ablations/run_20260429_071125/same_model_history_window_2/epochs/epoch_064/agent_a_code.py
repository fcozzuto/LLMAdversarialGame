def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target: resource where we can beat opponent most; if none, move to central/lower-risk.
    best_t = None
    best_v = -10**18
    if resources:
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd  # positive means we are closer
            # Prefer taking wins; otherwise prefer resources nearer and not too late.
            v = lead * 100 - myd
            # Deterministic tie-breaker
            v += (w - 1 - rx) - (h - 1 - ry) * 0.001
            if v > best_v:
                best_v = v
                best_t = (rx, ry)
    else:
        best_t = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = best_t
    # Candidate move deltas (deterministic order)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    myd0 = cheb(sx, sy, tx, ty)
    opd0 = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)

        # If opponent is closer to target, prioritize blocking by reducing their advantage (increase myd0-myd).
        # If we are closer, prioritize shortening path and avoid increasing distance to target.
        lead_after = opd - myd
        step_gain = (myd0 - myd)  # positive if getting closer
        # Slightly avoid stepping into squares that are "too close" to opponent to reduce immediate contest.
        opp_prox = cheb(nx, ny, ox, oy)
        score = lead_after * 100 + step_gain * 10 + opp_prox * 0.01

        # Mild preference for moves that go generally toward the target (stable in ties).
        score += (abs(nx - tx) <= abs(sx - tx) and abs(ny - ty) <= abs(sy - ty)) * 0.001

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]