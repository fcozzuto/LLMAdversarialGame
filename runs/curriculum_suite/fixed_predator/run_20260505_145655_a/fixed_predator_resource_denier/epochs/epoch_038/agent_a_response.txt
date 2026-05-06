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
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_sc = -10**18

    # Score: strong preference to resources where we are closer than opponent, plus slight preference for nearby targets.
    # Also add a small "interference" term: move direction that makes it harder for opponent to reach the same resource soon.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        local = -10**18
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Out-approach factor dominates; penalize being far; encourage getting within 1-2 steps.
            adv = (od - sd)
            sc = adv * 8 - sd
            if sd == 0:
                sc += 200
            elif sd == 1:
                sc += 18
            elif sd == 2:
                sc += 6
            # If opponent is much closer, don't commit unless we can still improve.
            if adv < 0:
                sc += adv * 2
            # Interference: reward moving so that opponent's distance to the same resource is relatively large compared to ours.
            sc += (od - (abs(sx - rx) + abs(sy - ry))) * 0.25
            if sc > local:
                local = sc

        if local > best_sc:
            best_sc = local
            best = [dx, dy]

    return [int(best[0]), int(best[1])]