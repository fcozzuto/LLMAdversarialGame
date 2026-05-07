def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_best_target(px, py):
        if not resources:
            return None, None, None
        best_adv = -10**18
        best_myd = 10**18
        best = None
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv or (adv == best_adv and (myd < best_myd or (myd == best_myd and (rx, ry) < best))):
                best_adv, best_myd, best = adv, myd, (rx, ry)
        return best, best_adv, best_myd

    best_move = (0, 0)
    best_val = -10**30
    any_valid = False

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        any_valid = True
        tgt, adv, myd = pick_best_target(nx, ny)
        if tgt is None:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val = -cheb(nx, ny, cx, cy) - 0.1 * cheb(nx, ny, ox, oy)
        else:
            # Prefer taking resources we're closer to than opponent; otherwise contest by maximizing opponent delay.
            val = adv * 1000 - myd * 3
            # Small preference to not drift away when clearly losing contests.
            if adv < 0:
                val += adv * 50
            # Encourage moving directly toward the chosen target.
            tx, ty = tgt
            val += -(abs(nx - tx) + abs(ny - ty)) * 0.5
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if not any_valid:
        return [0, 0]
    return [best_move[0], best_move[1]]