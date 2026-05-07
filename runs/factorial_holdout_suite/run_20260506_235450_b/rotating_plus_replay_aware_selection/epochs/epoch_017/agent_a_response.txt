def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Opponent likely target (nearest by Chebyshev).
    opp_target = resources[0]
    best_do = cheb(ox, oy, int(opp_target[0]), int(opp_target[1]))
    for r in resources[1:]:
        rx, ry = int(r[0]), int(r[1])
        d = cheb(ox, oy, rx, ry)
        if d < best_do:
            best_do, opp_target = d, r
    otx, oty = int(opp_target[0]), int(opp_target[1])

    best_move = (0, 0, -10**9, 0)
    for dx, dy, nx, ny in legal:
        best_adv = -10**9
        best_dself = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            if adv > best_adv or (adv == best_adv and d_self < best_dself):
                best_adv, best_dself = adv, d_self
        # Primary: take a resource where we are closer than opponent.
        # Secondary (if none): rush the opponent's nearest resource to steal soon.
        d_self_ot = cheb(nx, ny, otx, oty)
        score = best_adv * 100 - best_dself + (-d_self_ot)
        cand = (dx, dy, score, d_self_ot)
        if cand[2] > best_move[2] or (cand[2] == best_move[2] and (cand[0], cand[1]) < (best_move[0], best_move[1])):
            best_move = cand

    return [int(best_move[0]), int(best_move[1])]