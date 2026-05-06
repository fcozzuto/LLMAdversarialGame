def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # If no resources, drift to center to be hard to deny
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and ok(nx, ny):
            return [dx, dy]
        # fallback: any valid move that reduces dist to center
        best = (10**18, 0, 0)
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and ok(nx, ny):
                d = dist2(nx, ny, tx, ty)
                if d < best[0]:
                    best = (d, mx, my)
        return [best[1], best[2]]

    best_move = [0, 0]
    best_val = -10**18

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (inb(nx, ny) and ok(nx, ny)):
            continue

        # Evaluate best "contested" resource from this next position
        cur_best_adv = -10**18
        cur_best_selfd = 10**18
        for rx, ry in resources:
            selfd = dist2(nx, ny, rx, ry)
            oppd = dist2(ox, oy, rx, ry)
            # Prefer resources that are relatively closer to us than to opponent
            adv = oppd - selfd
            if oppd <= selfd:
                # If opponent is already at/near the resource, reduce commitment unless we're very close
                adv -= 3 * selfd
            if adv > cur_best_adv or (adv == cur_best_adv and selfd < cur_best_selfd):
                cur_best_adv = adv
                cur_best_selfd = selfd

        # Tie-break: slightly prefer being closer even if advantage is similar
        val = cur_best_adv - 0.02 * cur_best_selfd

        if val > best_val:
            best_val = val
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]