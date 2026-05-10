def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_set.add((int(r[0]), int(r[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    def cell_blocked(x, y):
        return (x, y) in obstacles

    def score_for_pos(px, py):
        best_adv = -10**9
        best_self_dist = 10**9
        best_hit = False
        for rx, ry in res_set:
            self_d = abs(rx - px) + abs(ry - py)
            opp_d = abs(rx - ox) + abs(ry - oy)
            adv = opp_d - self_d
            if self_d < best_self_dist:
                best_self_dist = self_d
            if adv > best_adv:
                best_adv = adv
            if (px, py) == (rx, ry):
                best_hit = True
        return (best_adv + (5 if best_hit else 0), -best_self_dist)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if cell_blocked(nx, ny):
            nx, ny = sx, sy
        sc = score_for_pos(nx, ny)
        if best is None or sc > best[0]:
            best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]