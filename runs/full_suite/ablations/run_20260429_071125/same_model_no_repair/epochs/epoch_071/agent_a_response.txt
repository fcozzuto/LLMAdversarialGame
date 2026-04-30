def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or []) if p and (p[0], p[1]) not in obstacles]

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best, bestv = (0, 0), -10**18
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, tx, ty) - 0.35 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    cur_res_min = 10**18
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < cur_res_min:
            cur_res_min = d
    if cur_res_min == 0:
        return [0, 0]

    best, bestv = (0, 0), -10**18
    for dx, dy, nx, ny in legal:
        # Choose the best next-step "race" outcome: get closer to a resource while making it harder for opponent.
        best_race = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # ds smaller is good; do smaller is bad (opponent can contest).
            race = (cur_res_min - ds) * 1.7 + (ds == 0) * 6.0 - (do - ds) * 0.55
            best_race = race if race > best_race else best_race
        # Slightly avoid stepping into cells that are adjacent to many resources.
        adj_pen = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) == 1:
                adj_pen += 1
        # Keep some spacing from opponent unless it blocks their contest.
        sep = cheb(nx, ny, ox, oy)
        v = best_race - adj_pen * 0.08 + sep * 0.02
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]