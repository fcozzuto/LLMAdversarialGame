def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    res = [(int(p[0]), int(p[1])) for p in resources]

    def best_value(px, py):
        # Larger is better: win capture races first, then prefer nearer resources
        best = None
        for rx, ry in res:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If my distance is smaller, I "own" the race; reward that strongly.
            v = (opd - myd) * 1000 - myd
            tiebreak = -myd
            if best is None or (v, tiebreak) > best:
                best = (v, tiebreak)
        return best[0]

    # Two-step deterministic lookahead: choose move that maximizes best_value after my move
    best_move = (0, 0)
    best_score = -10**18
    # If I am already closest to some resource, bias toward it.
    pre = []
    for rx, ry in res:
        pre.append((cheb(sx, sy, rx, ry) - cheb(ox, oy, rx, ry), cheb(sx, sy, rx, ry), rx, ry))
    pre.sort()
    focus = pre[0][2:]  # (rx, ry) of best "race edge" cell

    # Prefer not to drift if focus is reachable quickly
    for dx0, dy0 in deltas:
        nsx, nsy = sx + dx0, sy + dy0
        if not inb(nsx, nsy):
            nsx, nsy = sx, sy

        s = best_value(nsx, nsy)

        # Tie-breaking: move that decreases distance to focus and keeps me winning if possible
        frx, fry = focus
        s -= cheb(nsx, nsy, frx, fry) * 2
        s += cheb(ox, oy, frx, fry) * 0.5  # slight bias toward race-accessible region

        # If standing still while a capture is immediate and winning, allow stay; else compare normally.
        if (dx0, dy0) == (0, 0):
            # small penalty unless it doesn't worsen the best capture value
            s -= 1

        if s > best_score:
            best_score = s
            best_move = (dx0, dy0)

    dx, dy = best_move
    if dx == 0 and dy == 0:
        # If two-step lookahead was indecisive, ensure we at least move toward any resource we can reach first.
        rx, ry = focus
        best = (cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry), cheb(sx, sy, rx, ry))
        # Move to reduce my cheb to that resource
        best_d = None
        for dx0, dy0 in deltas:
            nsx, nsy = sx + dx0, sy + dy0
            if not inb(nsx, nsy):
                nsx, nsy = sx, sy
            d = cheb(nsx, nsy, rx, ry)
            if best_d is None or d < best_d:
                best_d = d
                dx, dy = dx0, dy0
    return [int(dx), int(dy)]