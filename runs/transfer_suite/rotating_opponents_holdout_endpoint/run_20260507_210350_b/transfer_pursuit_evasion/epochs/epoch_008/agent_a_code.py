def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = "pursuer" in sr
    opp_is_pursuer = "pursuer" in orr
    pursuer = i_am_pursuer or (not i_am_pursuer and not opp_is_pursuer and "pursuer" in (observation.get("environment_name") or "").lower())

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Evader: maximize distance from pursuer; if tied, move toward safer corner.
    # Pursuer: minimize distance; if tied, move toward opponent while preferring open lines.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Obstacle proximity penalty to discourage skimming walls (helps evader, helps pursuer not get trapped).
        prox = 0
        for ox2, oy2 in obs:
            t = abs(nx - ox2) + abs(ny - oy2)
            if t == 0: 
                prox = 10**9
                break
            if t <= 2:
                prox += (3 - t)
        if prox >= 10**8:
            continue

        if pursuer:
            # primary: reduce distance
            # secondary: prefer moving toward nearest corner that also minimizes distance to opponent
            c = min(corners, key=lambda p: cheb(nx, ny, p[0], p[1]))
            score = (d, cheb(c[0], c[1], ox, oy), prox, abs(nx - ox) + abs(ny - oy))
            key = score
            better = (best is None) or (key < best)
        else:
            # primary: increase distance
            # secondary: move toward farthest corner and away from obstacles
            c = max(corners, key=lambda p: cheb(nx, ny, p[0], p[1]))
            score = (-d, -cheb(c[0], c[1], ox, oy), prox, abs(nx - sx) + abs(ny - sy))
            key = score
            better = (best is None) or (key < best)

        if better:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]