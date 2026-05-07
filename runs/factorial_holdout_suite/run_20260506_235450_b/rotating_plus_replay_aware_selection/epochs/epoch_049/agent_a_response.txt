def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    resource_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resource_set.add((int(r[0]), int(r[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = (-10**9, 0, 0)
    rem = int(observation.get("remaining_resource_count", len(resources)) or 0)
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we can capture immediately, always prioritize.
        imm = 1 if (nx, ny) in resource_set else 0

        # Race heuristic: maximize (opponent distance - self distance) to best attainable resource.
        best_adv = -10**9
        tie = 10**9
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher => we arrive no later than opponent
            # In late game, prioritize closer finishing (smaller ds); early, prioritize secure wins (adv).
            finish_bias = -ds if rem <= 6 else -0.15 * ds
            opp_rush = 0.0 if adv >= 0 else 0.25 * adv  # penalize resources we're slower for
            v = adv + finish_bias + opp_rush

            # Prefer a resource where we are at least not slower; tie-break with smaller ds, then center.
            adv_key = v
            ds_key = ds
            center_key = abs(rx - center_x) + abs(ry - center_y)
            cand = (adv_key, -ds_key, -center_key)

            # Convert cand to scalar for deterministic comparison
            if (adv_key, -ds_key, -center_key) > (best_adv, -tie, 0):
                best_adv = adv_key
                tie = ds_key

        center_pos = abs(nx - center_x) + abs(ny - center_y)
        score = (imm * 1e6) + (best_adv * (2.0 if rem <= 6 else 1.0)) + (-0.05 * center_pos)

        if (score, -imm, -tie) > (best[0], best[1], best[2]):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]