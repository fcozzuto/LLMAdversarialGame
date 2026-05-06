def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    # Line control point: closer to the midpoint between agents than opponent is
    mx, my = (sx + ox) / 2.0, (sy + oy) / 2.0

    best_dx, best_dy = 0, 0
    best_val = -10**18

    # If we can see resources, race by tempo gap; otherwise, move into control mid.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        # Control/anti-run: encourage being closer to the midpoint than opponent
        my_mid = (nx - mx) * (nx - mx) + (ny - my) * (ny - my)
        opp_mid = (ox - mx) * (ox - mx) + (oy - my) * (oy - my)
        val += (opp_mid - my_mid) * 0.6

        if resources:
            # Main term: sum positive tempo advantages vs all resources, with gentle preference for nearer ones
            tempo = 0.0
            dist_self = 0.0
            dist_opp = 0.0
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Advantage if we can get there sooner than opponent from their current position
                gap = do - ds
                wgt = 1.0 / (1.0 + ds)
                tempo += gap * wgt
                dist_self += ds * 0.02
                dist_opp += do * 0.01
            val += tempo * 1.8
            # Micro preference: reduce own distance to the currently best target while increasing opponent distance from it
            nearest = min(resources, key=lambda p: man(nx, ny, p[0], p[1]))
            trx, try_ = nearest
            val += (man(ox, oy, trx, try_) - man(nx, ny, trx, try_)) * 0.9
            val -= dist_self + dist_opp * 0.3
        else:
            # No resources: move toward center of grid while still contesting midpoint
            val += -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.02

        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]