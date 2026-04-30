def choose_move(observation):
    me = observation["self_position"]
    opp = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((o[0], o[1]) for o in obstacles)

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        best_r = None
        best_key = None
        for r in resources:
            rx, ry = r
            if (rx, ry) in obs:
                continue
            dm = cheb(me, (rx, ry))
            do = cheb(opp, (rx, ry))
            # Prefer resources we're closer to; also prefer ones that opponent isn't already extremely close to.
            key = ((do - dm) * 1000 + (do - dm) * 10 + (10 - dm), -do, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        target = best_r if best_r is not None else (w // 2, h // 2)
    else:
        # No resources: move to center but keep distance from opponent.
        target = (w // 2, h // 2)

    tx, ty = target
    cx = opp[0] - me[0]
    cy = opp[1] - me[1]

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = me[0] + dx, me[1] + dy
        if not inb(nx, ny):
            continue
        nm = cheb((nx, ny), (tx, ty))
        no = cheb(opp, (tx, ty))
        adv = no - nm  # immediate advantage if we get closer while opponent stays
        my_opp_dist_after = cheb((nx, ny), opp)
        # Penalty: moving in the general direction of opponent
        toward_opp = 0
        if dx == 0 and (cx == 0 or cy == 0):
            toward_opp = 0
        if (dx != 0 and (dx * cx) > 0) or (dy != 0 and (dy * cy) > 0):
            toward_opp = 1
        key = (adv, my_opp_dist_after, -nm, -toward_opp, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]