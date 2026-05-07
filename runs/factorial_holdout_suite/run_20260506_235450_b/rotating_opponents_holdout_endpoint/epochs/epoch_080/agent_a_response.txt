def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    tr = int(observation.get("remaining_resource_count", 999) or 999)
    endgame = tr <= 5

    best = None
    best_score = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources we can secure earlier; in endgame, prioritize absolute closeness.
        score = (od - sd) * 10 + (20 - sd) + (5 if endgame else 0) - (3 if od < sd else 0)
        if best_score is None or score > best_score:
            best_score = score
            best = (x, y)

    # If opponent is significantly closer everywhere, shift to potential denial by moving toward their nearest.
    if best is not None:
        we_ahead = False
        for x, y in resources:
            if cheb(sx, sy, x, y) <= cheb(ox, oy, x, y) - 1:
                we_ahead = True
                break
        if not we_ahead:
            apick = None
            apd = None
            for x, y in resources:
                d = cheb(ox, oy, x, y)
                if apd is None or d < apd:
                    apd = d
                    apick = (x, y)
            if apick is not None:
                best = apick

    tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_m = (0, 0)
    best_m_score = None
    cur_d = cheb(sx, sy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer decreasing distance; slight preference for approaching while not giving opponent too much.
        opp_nd = cheb(ox, oy, tx, ty)
        mscore = (cur_d - nd) * 100 - nd * 2 - (1 if endgame and nd == 0 else 0) + (opp_nd - cheb(ox, oy, tx, ty)) * 0
        if best_m_score is None or mscore > best_m_score:
            best_m_score = mscore
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]