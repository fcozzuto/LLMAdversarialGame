def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    resources = [(x, y) for x, y in resources if (x, y) not in obs]
    if not resources:
        return [0, 0]

    def opp_target():
        best = None
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            key = (d, rx + ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = opp_target()

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = None

    for dx0, dy0 in candidates:
        nx, ny = sx + dx0, sy + dy0
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)

        # Deny opponent by pushing towards their likely target while making it harder for us to lose it.
        # Also softly keep our options open by looking at the best alternative resource.
        best_alt = None
        second_alt = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if best_alt is None or d < best_alt:
                second_alt = best_alt
                best_alt = d
            elif second_alt is None or d < second_alt:
                second_alt = d

        # Higher is better.
        # - prefer reducing our distance to the contested target (self_d)
        # - prefer increasing distance between opponent and contested target (via our proximity/cheb geometry)
        # - prefer having a near alternative after taking it (second_alt)
        score = (-(self_d * 2) - (best_alt if best_alt is not None else 0) + (opp_d * 0.2))
        if second_alt is not None:
            score += -0.15 * second_alt

        # Deterministic tie-break: smaller (nx+ny), then lexicographic.
        tie = (score, -(nx + ny), -dx0, -dy0)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = (dx0, dy0)

    return [best_move[0], best_move[1]]