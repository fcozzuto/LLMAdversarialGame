def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best = (-10**18, (0, 0))
    # Deterministic tie-break order by dirs already.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate best target resource for gaining tempo over opponent.
        best_adv = -10**18
        best_my = 10**9
        best_opp = 10**9
        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            if adv > best_adv or (adv == best_adv and my_d < best_my) or (adv == best_adv and my_d == best_my and opp_d < best_opp):
                best_adv = adv
                best_my = my_d
                best_opp = opp_d

        # Encourage closer to target and discourages stepping away.
        # Weight advantage heavily to race opponent.
        score = best_adv * 100 - best_my + (best_opp - best_my) * 0.5
        if score > best[0]:
            best = (score, (dx, dy))

    return [best[1][0], best[1][1]]