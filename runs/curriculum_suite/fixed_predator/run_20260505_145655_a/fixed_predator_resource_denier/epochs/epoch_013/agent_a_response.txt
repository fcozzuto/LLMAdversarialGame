def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)

    # Score combines (1) our closeness, (2) our advantage over opponent for that resource,
    # (3) a "denial" term favoring states that reduce opponent's best reach.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        our_best = -(10**18)
        our_sum = 0.0
        opp_best_at = -(10**18)

        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            adv = od - sd  # positive means we are closer than opponent
            # "denial" prefers increasing minimal advantage and also strong advantage on any target
            local = adv * 6 - sd
            if local > our_best:
                our_best = local
            # Smooth focus on near resources: larger when we are close; also increases with advantage
            our_sum += (adv + 1) / (1 + sd) - 0.15 * od / (1 + od)

            # Estimate how good opponent's current best target is; constant-ish but keeps ranking stable
            opp_best_at = max(opp_best_at, (sd - od) * 2 - od * 0.02)

        # If we are much closer than opponent to some resource, prioritize heavily.
        # Also include small preference for staying away from being "behind" everywhere.
        min_adv = 10**9
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            a = od - sd
            if a < min_adv:
                min_adv = a

        score = our_best + 1.5 * our_sum + 0.9 * min_adv - 0.01 * opp_best_at
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]