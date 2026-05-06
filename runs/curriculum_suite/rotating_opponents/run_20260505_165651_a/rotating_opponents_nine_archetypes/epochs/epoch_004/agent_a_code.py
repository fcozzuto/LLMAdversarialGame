def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    res_set = set(resources)
    best = None  # (score, -on_res, tie_x, tie_y, dx, dy)

    # Prefer safe progress toward a resource while preventing opponent capture nearby.
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue

        on_res = 1 if (nx, ny) in res_set else 0

        # Choose resource that maximizes our advantage from this candidate cell.
        best_adv = -10**18
        best_rx = best_ry = None
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Prefer closer resource; also prefer resources that opponent is farther from.
            # Small deterministic tie by resource coordinates.
            adv = (opp_d - our_d) * 10 - our_d
            if adv > best_adv or (adv == best_adv and (rx, ry) < (best_rx, best_ry)):
                best_adv = adv
                best_rx, best_ry = rx, ry

        # Avoid moving into opponent vicinity (center_rush tends to collide head-on).
        d_op = man(nx, ny, ox, oy)
        avoid = 0
        if d_op <= 2:
            avoid = -(3 - d_op) * 25
        elif d_op == 3:
            avoid = -10

        # Mild preference for moving toward board center to counter center_rush.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - cx) + abs(ny - cy)
        center_bonus = -center_dist

        score = best_adv + on_res * 200 + avoid + center_bonus
        cand = (score, -on_res, nx, ny, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[4], best[5]]