def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a resource that maximizes our reach advantage over the opponent (different from "always nearest").
    best_r = None
    best_adv = -10**9
    best_ds = 10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and ds < best_ds):
            best_adv = adv
            best_ds = ds
            best_r = (rx, ry)

    if best_r is None:
        # No resources left: head to center while keeping safe.
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    # Evaluate candidate moves.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        d_after = cheb(nx, ny, tx, ty)
        d_opp_after = cheb(ox, oy, tx, ty)
        # Advantage after our move: opponent static, so maximizing (d_opp - d_after) helps race control.
        adv_after = d_opp_after - d_after

        # Mild obstacle proximity penalty to avoid getting boxed in.
        prox_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    prox_pen += 1

        # If we can step onto a resource, strongly prefer it.
        on_resource = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        val = (adv_after * 1000) - (d_after * 10) + (on_resource * 100000) - (prox_pen * 3)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]