def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose target by relative advantage: maximize (opp_dist - self_dist)
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    if best_t is None:
        best_t = (w // 2, h // 2)

    tx, ty = best_t

    def obst_pen(x, y):
        # Strongly discourage being adjacent to obstacles
        pen = 0
        for ax, ay in obstacles:
            if cheb(x, y, ax, ay) == 1:
                pen += 3
        return pen

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue

        ds_new = cheb(nx, ny, tx, ty)
        do_new = cheb(ox, oy, tx, ty)

        # Advantage over target plus "deny" term: we want to increase our advantage and decrease theirs.
        val = (do_new - ds_new) * 50 - ds_new * 2

        # Deny term across all resources: move that reduces opponent access more is favored.
        deny = 0
        for rx, ry in resources[:12]:
            ds0 = cheb(sx, sy, rx, ry)
            do0 = cheb(ox, oy, rx, ry)
            ds1 = cheb(nx, ny, rx, ry)
            do1 = cheb(ox, oy, rx, ry)
            # If we move closer while they stay, we deny indirectly by changing who likely gets next.
            deny += (do0 - ds1) - (do0 - ds0)
        val += deny * 6

        # Avoid stepping into/near obstacles
        val -= obst_pen(nx, ny)

        # Tiny deterministic tie-break favoring staying direction toward target (lexicographic already stable by loop order)
        dist_now = cheb(sx, sy, tx, ty)
        dist_then = cheb(nx, ny, tx, ty)
        val += (dist_now - dist_then)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]