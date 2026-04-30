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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 0 if sx > w // 2 else w - 1
        ty = 0 if sy > h // 2 else h - 1
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            adv = cheb(ox, oy, tx, ty) - d
            cand = (d, -adv, dy, dx)
            if cand < best:
                best = cand
        return [int(best[3]), int(best[2])]

    opp_reach_bias = 2.0
    best_score = -10**18
    best_move = [0, 0]
    my_opp_pref = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_dmin = 10**9
        opp_dmin_for_that = 10**9
        for rx, ry in resources:
            d_m = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            if d_m < my_dmin:
                my_dmin = d_m
                opp_dmin_for_that = d_o
            elif d_m == my_dmin and d_o < opp_dmin_for_that:
                opp_dmin_for_that = d_o

        # Try to win the closest contested resource race; penalize moving away if already close.
        contested_adv = opp_dmin_for_that - my_dmin
        score = -my_dmin + opp_reach_bias * contested_adv

        # Mildly increase distance from opponent when no clear advantage
        if contested_adv <= 0:
            score += 0.01 * (cheb(nx, ny, ox, oy) - my_opp_pref)

        # Deterministic tiebreak: prefer lower dx then dy based on fixed order
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]