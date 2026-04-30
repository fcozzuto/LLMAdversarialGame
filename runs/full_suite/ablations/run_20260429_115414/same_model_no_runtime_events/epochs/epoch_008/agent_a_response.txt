def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)
    res = [(p[0], p[1]) for p in resources if p is not None and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    oppd_map = {}  # not used; kept minimal

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # immediate safety: discourage walking into opponent's next optimal contact
        d_opp_next = man(nx, ny, ox, oy)

        # choose best resource target for this move
        if res:
            local_best = -10**18
            # deterministic resource ordering by coordinates
            for (rx, ry) in sorted(res, key=lambda t: (t[0], t[1])):
                myd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # prefer capturing now, then getting to resource before opponent
                val = 0
                if (nx, ny) == (rx, ry):
                    val += 100000
                # advantage over opponent on same target
                val += (od - myd) * 120
                # slight preference to be close (ties broken by advantage)
                val += -myd
                # if resource is behind opponent (i.e., opponent already closer), penalize
                if od < myd:
                    val += -50 * (myd - od)
                if val > local_best:
                    local_best = val
            v = local_best - 2 * d_opp_next
        else:
            # no visible resources: drift to increase chances while staying away from opponent
            v = -d_opp_next

        # deterministic tie-break: prefer smaller dx,dy in scan order already, but ensure stable
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]