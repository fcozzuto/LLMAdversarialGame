def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # deterministic fallback: move toward center-ish, away from opponent slightly
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (-10**18, 0, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dcen = dist_cheb(nx, ny, int(round(cx)), int(round(cy)))
            dopp = dist_cheb(nx, ny, ox, oy)
            score = (-dcen) + 0.01 * dopp
            tie = (dx, dy)
            if score > best[0] or (score == best[0] and tie < (best[2], best[3])):
                best = (score, 1, dx, dy)
        return [best[2], best[3]]

    # Evaluate moves by the best "advantage" over opponent for any resource after this move.
    # Advantage: (opp_dist - my_dist_next), so higher is better.
    best_score = -10**18
    best_move = [0, 0]
    best_mdist = 10**9
    best_lex = (9, 9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best_adv = -10**18
        my_best_mdist = 10**9
        for rx, ry in resources:
            md = dist_cheb(nx, ny, rx, ry)
            od = dist_cheb(ox, oy, rx, ry)
            adv = od - md
            if adv > my_best_adv or (adv == my_best_adv and md < my_best_mdist):
                my_best_adv = adv
                my_best_mdist = md
        # Prefer moves that also reduce closest-to-opponent threat (small secondary)
        dopp_after = dist_cheb(nx, ny, ox, oy)
        score = my_best_adv + 0.001 * dopp_after - 0.0005 * my_best_mdist
        lex = (dx, dy)
        if score > best_score or (score == best_score and (my_best_mdist < best_mdist or (my_best_mdist == best_mdist and lex < best_lex))):
            best_score = score
            best_move = [dx, dy]
            best_mdist = my_best_mdist
            best_lex = lex
    return best_move