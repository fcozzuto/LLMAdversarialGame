def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, cx, cy)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Interception: target the resource nearest to opponent, then move to beat them there.
    def lex_key(p):
        return (p[0], p[1])

    opp_target = min(resources, key=lambda r: (cheb(r[0], r[1], ox, oy), lex_key(r)))
    tx, ty = opp_target

    # Also add slight preference for closing to our nearest resource to prevent stalls.
    my_nearest = min(resources, key=lambda r: (cheb(r[0], r[1], sx, sy), lex_key(r)))
    mx, my = my_nearest

    legal.sort()
    best = legal[0]
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        self_to_t = cheb(nx, ny, tx, ty)
        opp_to_t_next = cheb(ox, oy, tx, ty)  # we don't know their move; approximate by current

        self_to_m = cheb(nx, ny, mx, my)

        # Primary: minimize our distance advantage deficit vs opponent's likely target.
        # Secondary: aggressively reduce distance to their target.
        # Tertiary: reduce distance to our nearest resource to avoid deadlocks.
        score = (opp_to_t_next - self_to_t) * 100 - self_to_t * 2 - self_to_m

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]