def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If a resource is currently "contested" (equal distance), try to get closer to win it.
    best_move = (0, 0)
    best_val = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            nx, ny = sx, sy

        # Evaluate by best resource for us after this move, considering opponent distance to that same resource.
        # Prefer: larger (opp_dist - our_dist) with a penalty for our distance (to actually reach).
        val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Tie-breakers: get the resource earlier; also slightly prefer resources closer to opponent (to deny).
            pr = (do - ds) * 6 - ds * 1
            if ds == do:
                pr += 2  # contested: moving closer can swing
            # Encourage denying nearest opponent target: if we can beat them by 1, boost more.
            if do - ds >= 1:
                pr += 1
            if pr > val:
                val = pr

        # Small tie-break: don't drift away from center-ish of remaining resources.
        if observation.get("remaining_resource_count") is not None:
            rc = int(observation.get("remaining_resource_count") or 0)
        else:
            rc = len(resources)
        if rc <= 4:
            # late game: reduce our closest distance
            mind = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            val -= mind * 0.1
        if val > best_val:
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]