def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        # Prefer staying or stepping away from opponent slightly to avoid being "rushed"
        best = None
        for dx, dy, nx, ny in legal:
            score = (cheb(nx, ny, ox, oy), cheb(nx, ny, sx, sy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Target selection: maximize our advantage (opponent distance - our distance), then finish soon, then deterministic index.
    bestT = None
    bestLead = -10**9
    for i, (rx, ry) in enumerate(resources):
        if (rx, ry) in obst:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # If opponent is closer, heavily down-rank to force a materially different direction than previous epochs.
        # If we're not winning on this resource, prefer resources where we are at least not behind by more than 1 step.
        penalty = 0
        if ds > do:
            penalty = 1000 + (ds - do) * 10
        elif do == ds:
            penalty = 5
        score = (-(lead) + penalty, ds, do, i)
        if bestT is None or score < bestT[0]:
            bestT = (score, rx, ry, ds, do)
            bestLead = lead

    _, tx, ty, ds0, do0 = bestT

    # Move choice: greedy toward target, but if opponent is much closer to the target, try to "shadow" by increasing opponent-target distance.
    oppFocus = (do0 - ds0) < 1  # opponent is close/even
    bestM = None
    for dx, dy, nx, ny in legal:
        nds = cheb(nx, ny, tx, ty)
        # Main: minimize distance to target.
        # Secondary: if opponent is close to the same target, maximize opponent distance to that target (intercept/deny).
        if oppFocus:
            nodo = cheb(ox, oy, tx, ty)
            oppDistScore = -cheb(ox, oy, tx, ty)  # constant-ish, but keeps form deterministic
            den = -cheb(ox, oy, nx, ny)     # avoid clustering directly with opponent
            score = (nds, -cheb(nx, ny, ox, oy), den)
        else:
            # Normal: avoid getting closer to opponent while progressing to target.
            score = (nds, -cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy))
        # Deterministic tie-breaker: prefer smallest dx, then dy
        score = (score[0], score[1], score[2], abs(dx) + abs(dy), dx, dy)
        if bestM is None or score < bestM[0]:
            bestM = (score, dx, dy)

    return [bestM[1], bestM[2]]