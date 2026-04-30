def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal_from(px, py):
        out = []
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy, nx, ny))
        return out

    my_legal = legal_from(sx, sy)
    if not my_legal:
        return [0, 0]

    # No resources left: maximize escape distance from opponent to a corner.
    if not resources:
        tx = 0 if cheb(ox, oy, 0, 0) < cheb(ox, oy, w - 1, h - 1) else w - 1
        ty = 0 if cheb(ox, oy, 0, 0) < cheb(ox, oy, w - 1, h - 1) else h - 1
        best, bestv = (0, 0, sx, sy), -10**18
        for dx, dy, nx, ny in my_legal:
            v = cheb(nx, ny, tx, ty) - 0.15 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy, nx, ny)
        return [best[0], best[1]]

    # Choose a target resource where we currently have (or can create) advantage.
    best_res, best_adv = resources[0], -10**18
    for rx, ry in resources:
        adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
        # slight preference for closer absolute progress
        adv -= 0.02 * cheb(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv, best_res = adv, (rx, ry)
    tx, ty = best_res

    opp_legal = legal_from(ox, oy)

    # For each move, estimate opponent's best next distance to the target and our closeness.
    best, bestv = (0, 0, sx, sy), -10**18
    for dx, dy, nx, ny in my_legal:
        self_d = cheb(nx, ny, tx, ty)

        # opponent can move once toward the target; approximate by best achievable (min distance)
        opp_best_d = 10**9
        for odx, ody, onx, ony in opp_legal:
            d = cheb(onx, ony, tx, ty)
            if d < opp_best_d:
                opp_best_d = d

        # progress to alternative resources if target is blocked/contested
        alt_min = 10**9
        for