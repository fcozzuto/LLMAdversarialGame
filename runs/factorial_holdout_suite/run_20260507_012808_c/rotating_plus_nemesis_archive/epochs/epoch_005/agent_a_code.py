def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = [-10**9, [0, 0]]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            d = cheb(nx, ny, tx, ty)
            s = -d
            if s > best[0]:
                best = [s, [dx, dy]]
        return best[1]

    opp_all = [cheb(ox, oy, r[0], r[1]) for r in resources]
    best_score, best_move = -10**18, [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        my_min_d = 10**9
        my_best_adv = -10**9
        my_best_d = 10**9
        for i, r in enumerate(resources):
            my_d = cheb(nx, ny, r[0], r[1])
            if my_d < my_min_d:
                my_min_d = my_d
            adv = opp_all[i] - my_d
            if adv > my_best_adv or (adv == my_best_adv and my_d < my_best_d):
                my_best_adv, my_best_d = adv, my_d
        score = my_best_adv * 10 - my_best_d
        if score > best_score:
            best_score, best_move = score, [dx, dy]
    return best_move