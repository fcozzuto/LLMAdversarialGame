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

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]

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

    # If we are very close to any resource, prioritize collecting over repositioning.
    close = any(cheb(sx, sy, rx, ry) == 0 for rx, ry in res)
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_best = 10**9
        opp_best = 10**9
        best_adv = -10**9
        best_tie = 10**9

        for rx, ry in res:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md
            if adv > best_adv or (adv == best_adv and (md < my_best or (md == my_best and od < opp_best))):
                best_adv = adv
                my_best = md
                opp_best = od
                best_tie = md

        # Centering as a weak tiebreaker; also penalize moves that let opponent be strictly closer.
        center = -abs(nx - cx) - abs(ny - cy)
        urgency = 0 if close else 0.0
        score = (best_adv * 1000) - (my_best * 3) + (center * 0.1) - (0.5 if opp_best < my_best else 0.0) + urgency

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]