def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        resources = [(ox, oy)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_adj(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        return 1
        return 0

    best_targets = []
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # prefer close resources; penalize ones opponent is closer to
        best_targets.append((ds - 0.9 * do, tx, ty))
    best_targets.sort()
    target = (best_targets[0][1], best_targets[0][2])

    tx, ty = target

    # Try to move toward target; if opponent is also close, slightly prioritize reducing their advantage.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds_now = cheb(sx, sy, tx, ty)
        ds_next = cheb(nx, ny, tx, ty)

        do_next = cheb(nx, ny, ox, oy)
        opp_dist_to_target = cheb(ox, oy, tx, ty)

        # improvement toward our target + avoid obstacles + tactical "deny" if opponent not far
        val = (ds_now - ds_next) * 10
        val -= obs_adj(nx, ny) * 2
        # deny: if opponent is near this target, discourage staying away from reducing their reach
        val -= max(0, opp_dist_to_target - cheb(ox, oy, tx, ty)) * 0
        val -= (cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy)) * 0  # keep neutral
        # If opponent is closer to the target, be more aggressive (bigger weight on progress)
        if cheb(ox, oy, tx, ty) < cheb(sx, sy, tx, ty):
            val += (ds_now - ds_next) * 6
        # slight preference for moves that also move away from being too close to opponent
        val -= cheb(nx, ny, ox, oy) * 0.2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]