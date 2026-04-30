def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles") or [])
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = w // 2, h // 2
        best = (0, 0)
        best_sc = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = md(nx, ny, cx, cy)
            sc = -d - 0.01 * cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc, best = sc, (dx, dy)
        return [best[0], best[1]]

    # If opponent is close to any resource, contest it deterministically.
    contest = []
    for tx, ty in resources:
        if cheb(ox, oy, tx, ty) <= 2:
            contest.append((tx, ty))
    contest = contest if contest else resources

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Denial: prefer targets where opponent is farther than us, i.e., reduce their advantage.
        gain = -10**18
        closest_self = 10**9
        closest_opp = 10**9
        for tx, ty in resources:
            sg = cheb(nx, ny, tx, ty)
            og = cheb(ox, oy, tx, ty)
            g = og - sg
            if g > gain:
                gain = g
            if sg < closest_self:
                closest_self = sg
            if og < closest_opp:
                closest_opp = og

        # Contest: if opponent has nearby resource(s), get closer to one of them.
        contest_best = 10**9
        for tx, ty in contest:
            ds = cheb(nx, ny, tx, ty)
            if ds < contest_best:
                contest_best = ds

        # Simple blocking pressure: move to reduce distance to opponent when both are engaged.
        d_self_opp = cheb(nx, ny, ox, oy)
        engaged = 1 if (closest_opp <= 2) or any(cheb(ox, oy, tx, ty) <= 2 for tx, ty in resources) else 0

        sc = 12 * gain - 0.6 * contest_best - 0.05 * closest_self + (0.25 * engaged) - 0.02 * d_self_opp
        if sc > best_score:
            best_score, best_move = sc, (dx, dy)

    return [best_move[0], best_move[1]]