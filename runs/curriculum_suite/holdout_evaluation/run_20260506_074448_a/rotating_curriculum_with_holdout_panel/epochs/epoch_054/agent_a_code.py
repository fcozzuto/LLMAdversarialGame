def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def center_bias(x, y):
        dx = x - cx0
        dy = y - cy0
        return -(dx * dx + dy * dy) * 0.001

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if not resources:
            val = center_bias(nx, ny) - 0.0001 * man(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_dx, best_dy = dx, dy
            continue

        # Interception/race: pick best advantage over opponent for any resource.
        my_best_adv = -10**18
        my_best_dist = 10**9
        opp_best_dist = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            adv = oppd - myd
            # Prefer resources where we arrive first; also prefer tight races.
            if adv > my_best_adv or (adv == my_best_adv and myd < my_best_dist) or (adv == my_best_adv and myd == my_best_dist and oppd < opp_best_dist):
                my_best_adv = adv
                my_best_dist = myd
                opp_best_dist = oppd

        # Avoid giving opponent easy access to the resource we target:
        # if we are behind, discourage moves that shrink opponent advantage too much.
        behind_pen = 0.0
        if my_best_adv < 0:
            behind_pen = (-my_best_adv) * 1.5 + (my_best_dist * 0.05)
        else:
            # If we're ahead, still prefer closer resources and keep pressure.
            behind_pen = -min(my_best_adv, 10) * 0.3

        # Anticipate sweep-row behavior: gently move toward matching opponent row or column.
        row_align = -abs(ny - oy) * 0.02
        col_align = -abs(nx - ox) * 0.02

        val = (my_best_adv * 2.0) - my_best_dist * 0.15 - opp_best_dist * 0.01 + behind_pen + row_align + col_align + center_bias(nx, ny)

        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]