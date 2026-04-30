def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # If we can capture a resource this turn, do it (deterministic tie-break).
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(sx, sy, rx, ry)
            if ds <= 1:
                do = cheb(ox, oy, rx, ry)
                # Prefer resources we can take and that are relatively harder for opponent.
                key = (do - ds, -ds, rx, ry)
                if best is None or key > best[0]:
                    best = (key, rx, ry)
        if best is not None:
            rx, ry = best[1], best[2]
            dx = 0 if rx == sx else (1 if rx > sx else -1)
            dy = 0 if ry == sy else (1 if ry > sy else -1)
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
            # If blocked, fall through to greedy move.

    # Choose a target resource to maximize advantage: (opp_dist - self_dist).
    if resources:
        # Evaluate candidate target resources reachable in theory (ignore obstacles only for step checks).
        best_t = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher is better
            # Prefer closer/important resources when adv ties.
            key = (adv, -ds, rx, ry)
            if best_t is None or key > best_t[0]:
                best_t = (key, rx, ry)
        tx, ty = best_t[1], best_t[2]
    else:
        tx, ty = (w - 1, h - 1)  # deterministic fallback

    # Intercept/block: if opponent is much closer to the target, choose a "shadow" point:
    # move to reduce opponent progress by aiming at a cell near target on their side.
    if resources:
        ds_t = cheb(sx, sy, tx, ty)
        do_t = cheb(ox, oy, tx, ty)
        if do_t < ds_t:  # opponent closer; try to contest by targeting a near-tile of the resource
            # Choose a neighbor of target that is closest to opponent, to potentially cut them off.
            best_nei = None
            for dx2 in (-1, 0, 1):
                for dy2 in (-1, 0, 1):
                    if dx2 == 0 and dy2 == 0:
                        continue
                    nx, ny = tx + dx2, ty + dy2
                    if not inb(nx, ny) or (nx, ny) in obs:
                        continue
                    key = (cheb(sx, sy, nx, ny) - cheb(ox, oy, nx, ny), -cheb(sx, sy, nx, ny), nx, ny)
                    if best_nei is None or key > best_nei[0]:
                        best_nei = (key, nx, ny)
            if best_nei is not None:
                tx, ty = best_nei[1], best_nei[2]

    # Greedy step: maximize next advantage and keep safe (avoid obstacles).
    best_move = (None, 0, 0)  # (score, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = che