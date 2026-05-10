def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    my_candidates = [(dx, dy) for dx, dy in moves if ok(sx + dx, sy + dy)]
    opp_candidates = [(dx, dy) for dx, dy in moves if ok(ox + dx, oy + dy)]
    if not my_candidates:
        return [0, 0]

    def best_value(tx, ty):
        # Value targets by slack (how much closer we can be than the opponent)
        # Prefer also nearer targets (tie-breaker).
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        return (opd - myd, -myd, -tx, -ty)

    # Pick a small deterministic candidate set: best slack resources and nearest ones.
    scored = []
    for rx, ry in resources:
        scored.append((best_value(rx, ry), rx, ry))
    scored.sort(reverse=True)
    top = scored[: min(4, len(scored))]

    best_move = [0, 0]
    best_obj = None

    for _, tx, ty in top:
        for dx, dy in my_candidates:
            nx, ny = sx + dx, sy + dy
            myd_next = cheb(nx, ny, tx, ty)
            # Opponent "denier" approximation: assume they move to minimize their distance next turn.
            opd_next = None
            for odx, ody in opp_candidates:
                px, py = ox + odx, oy + ody
                d = cheb(px, py, tx, ty)
                if opd_next is None or d < opd_next:
                    opd_next = d
            if opd_next is None:
                opd_next = cheb(ox, oy, tx, ty)

            # Primary: maximize slack after our move; Secondary: minimize our distance; Tertiary deterministic.
            obj = (opd_next - myd_next, -myd_next, -dx, -dy, -tx, -ty)
            if best_obj is None or obj > best_obj:
                best_obj = obj
                best_move = [dx, dy]

    return best_move