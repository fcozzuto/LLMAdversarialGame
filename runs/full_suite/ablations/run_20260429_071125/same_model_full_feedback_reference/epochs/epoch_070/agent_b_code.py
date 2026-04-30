def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Choose a resource by maximizing "opponent minus us" (contested priority),
        # but with deterministic tie-breaking that favors proximity to us.
        best = None
        best_adv = -10**9
        best_our = 10**9
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d
            if adv > best_adv or (adv == best_adv and (our_d < best_our or (our_d == best_our and (rx + ry) < (best[0] + best[1] if best else 10**9)))):
                best_adv = adv
                best_our = our_d
                best = (rx, ry)
        tx, ty = best

    # Move greedily toward the chosen target, while discouraging giving the opponent progress.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our_d2 = cheb(nx, ny, tx, ty)
        opp_d2 = cheb(ox, oy, tx, ty)
        adv2 = opp_d2 - our_d2
        dist_opp = cheb(nx, ny, ox, oy)
        key = (our_d2, -adv2, -dist_opp, (dx, dy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]