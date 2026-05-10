def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obstacles

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = corners[(sx + 3 * sy) % 4]
        best = (-10**9, None)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            score = -md(nx, ny, tx, ty) + md(nx, ny, ox, oy)
            if score > best[0]:
                best = (score, [dx, dy])
        return best[1] if best[1] is not None else [0, 0]

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        sd = md(nx, ny, ox, oy)
        # Race to a resource: maximize opponent advantage (opp_dist - self_dist)
        # Then refine by closeness to the same resource and spacing from opponent.
        best_for_move = -10**18
        for rx, ry in resources:
            self_to = md(nx, ny, rx, ry)
            opp_to = md(ox, oy, rx, ry)
            race = opp_to - self_to
            val = race * 1000 - self_to - (sd // 2)
            if val > best_for_move:
                best_for_move = val
        if best_for_move > best_score:
            best_score = best_for_move
            best_move = [dx, dy]
    return best_move