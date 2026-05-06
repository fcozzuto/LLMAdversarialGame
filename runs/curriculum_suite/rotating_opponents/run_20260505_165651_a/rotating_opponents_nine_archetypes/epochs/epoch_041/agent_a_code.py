def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If no resources, stabilize near center while keeping away from obstacles via validity checks.
        if not resources:
            center_bias = -(abs(nx - cx) + abs(ny - cy))
            # also slightly reduce chance of giving opponent easy capture distance by moving away from them
            opp_bias = king_dist(nx, ny, ox, oy)
            val = center_bias + 0.01 * opp_bias
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
            continue

        # Choose the best contested resource for this move.
        best_adv = -10**18
        best_denial = -10**18
        for rx, ry in resources:
            ds = king_dist(nx, ny, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            # adv>0 means we can reach sooner than opponent
            adv = do - ds
            # denial favors stealing by making ds small even if we're behind
            denial = -ds + 0.25 * (do - ds)

            if adv > best_adv:
                best_adv = adv
            if denial > best_denial:
                best_denial = denial

        # Main objective: maximize advantage if possible; otherwise maximize denial.
        # Add small center and anti-commitment term to avoid drifting into losing races.
        center_term = -0.02 * (abs(nx - cx) + abs(ny - cy))
        opp_dist_term = -0.005 * king_dist(nx, ny, ox, oy)
        if best_adv > 0:
            val = 20.0 * best_adv + 0.1 * best_denial + center_term + opp_dist_term
        else:
            val = 5.0 * best_denial + center_term + opp_dist_term

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]