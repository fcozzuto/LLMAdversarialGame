def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res = [(r[0], r[1]) for r in resources]
    res_set = set(res)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (-(10**18), 0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        immediate = 1000000 if (nx, ny) in res_set else 0
        # After-move advantage: how much closer we are than opponent to the same resource.
        best_adv_for_move = -(10**18)
        for rx, ry in res:
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            # Prefer resources that we are (or would become) closer to; tie-break by closer self distance.
            adv = (opp_d - self_d) * 1000 - self_d
            # If we can pick up immediately, strongly dominate that resource selection.
            if (nx, ny) == (rx, ry):
                adv += 10**7
            if adv > best_adv_for_move:
                best_adv_for_move = adv
        # Small deterministic tie-break: prefer moves with smaller dx, then smaller dy.
        tie = -(abs(dx) * 10 + abs(dy))
        val = immediate + best_adv_for_move + tie
        if val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]