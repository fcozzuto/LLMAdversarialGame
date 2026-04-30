def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obs_list = observation.get('obstacles', [])
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a deterministic target: minimize "we can get it sooner than opponent"
    if resources:
        best = None
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer; discourage opponent access.
            # Corner bias: slightly prefer routes that move us away from opponent's corner.
            corner_bias = md(w - 1 - ox, h - 1 - oy, rx, ry) * 0.02
            val = (ds - 1.15 * do) + corner_bias
            if best is None or val < best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_val = -10**9

    # Evaluate each legal delta; obstacles are hard-blocked in our heuristic
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            ds_next = md(nx, ny, tx, ty)
            do_now = md(ox, oy, tx, ty)
            do_next = md(ox, oy, tx, ty)  # opponent doesn't move this turn in heuristic

            # Main objective: reduce our distance to target, while being ahead of opponent on it.
            advantage = (do_now - ds_next) * 1.5

            # Obstacle proximity penalty to avoid getting trapped near blocks.
            prox = 0
            for ax, ay in obs_list:
                prox += max(0, 2 - (abs(nx - ax) + abs(ny - ay)))
            prox_pen = prox * 0.6

            # Mild preference to progress from our side toward target.
            progress = md(sx, sy, tx, ty) - ds_next

            # Small tie-break favoring alignment with target (deterministic via integer parts)
            align = 0
            if dx != 0 and (tx - sx) * dx > 0:
                align += 1
            if dy != 0 and (ty - sy) * dy > 0:
                align += 1

            val = advantage + progress * 1.2 - ds_next * 0.25 - prox_pen + align * 0.01

            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    # If all moves were blocked (should be rare), stay.
    return best_move