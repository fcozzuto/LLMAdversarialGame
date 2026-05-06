def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Defense / no resources: move to intercept along the shortest approach direction to us
    if not resources:
        # pick move minimizing (distance to midpoint along line) and maximizing threat to opponent's approach
        mx, my = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            dmid = man(nx, ny, mx, my)
            do = man(nx, ny, ox, oy)
            # primary: reduce midpoint distance; secondary: keep distance to opponent (avoid getting pinned)
            key = (dmid, do)
            if bestv is None or key < bestv:
                bestv = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Resource contest heuristic:
    # For each move, choose the best resource and evaluate advantage approx:
    # self_effective = dist(self->res from new pos)
    # opp_effective  = dist(opp->res) - 1 (they can move next turn)
    best = (0, 0)
    bestv = None
    for dx, dy, nx, ny in moves:
        best_adv = -10**9
        best_res_d = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry) - 1
            adv = od - sd
            # prefer making adv larger; then prefer shorter self distance
            if adv > best_adv or (adv == best_adv and sd < best_res_d):
                best_adv = adv
                best_res_d = sd
        # avoid dead moves: slightly penalize moving away from all resources by using min self dist
        min_self = min(man(nx, ny, rx, ry) for rx, ry in resources)
        min_opp = min(man(ox, oy, rx, ry) for rx, ry in resources)
        # primary: maximize advantage; secondary: minimize self approach distance; tertiary: keep closer to resources than opponent
        key = (-best_adv, best_res_d, min_self - min_opp)
        if bestv is None or key < bestv:
            bestv = key
            best = (dx, dy)

    return [best[0], best[1]]