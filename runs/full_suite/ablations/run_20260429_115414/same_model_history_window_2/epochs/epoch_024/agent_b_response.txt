def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # No resources left: drift away deterministically.
    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            cand = (v, -dx, -dy)
            if best is None or cand > best[0]:
                best = (cand, dx, dy)
        return [best[1], best[2]]

    # Contested-resource targeting: maximize (opp_d - our_d), with landing bonus.
    # Also slightly prefer moves that reduce our distance to the single best contested resource.
    best_score = None
    best_move = (0, 0)
    order = 0
    for dx, dy, nx, ny in legal:
        order += 1
        on_res = 1 if (nx, ny) in map(tuple, resources) else 0
        our_best = 10**9
        opp_best = 10**9
        # evaluate best contested advantage among resources
        best_adv = -10**9
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = (opp_d - our_d)
            if adv > best_adv:
                best_adv = adv
                our_best = our_d
                opp_best = opp_d
        # Integer-scored heuristic: prefer advantage, then prefer closer our_best, avoid giving opponent too much.
        score = best_adv * 1000 + on_res * 5000 - our_best * 5 + opp_best * 0
        cand = (score, -dx, -dy, order)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]