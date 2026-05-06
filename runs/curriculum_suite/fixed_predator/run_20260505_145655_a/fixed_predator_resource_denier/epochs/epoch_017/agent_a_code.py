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
    best = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Two-level deterministic heuristic:
        # 1) Maximize out-approach advantage over opponent for some resource.
        # 2) If no resource is favorable, minimize own distance to the best "reachable" resource.
        local_best = -10**18
        local_best_self = 10**18
        local_best_opp = 10**18

        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            adv = oppd - selfd  # positive means we are closer (or winning that resource race)
            # Strongly prefer winning/denying races; then prefer shorter self distance.
            sc = adv * 12 - selfd
            if selfd == 0:
                sc += 10**6
            if sc > local_best:
                local_best = sc
                local_best_self = selfd
                local_best_opp = oppd
            elif sc == local_best:
                # Tie-break: prefer smaller self distance, then larger opponent distance
                if selfd < local_best_self or (selfd == local_best_self and oppd > local_best_opp):
                    local_best_self = selfd
                    local_best_opp = oppd

        # Additional penalty for moving next to obstacles (helps stability vs deniers/interceptors)
        # while remaining deterministic and cheap.
        near_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            tx, ty = nx + ax, ny + ay
            if in_bounds(tx, ty) and (tx, ty) in obstacles:
                near_obs += 1

        total = local_best - near_obs * 0.7 + (0.05 if (dx == 0 and dy == 0) else 0.0)
        if total > best_score:
            best_score = total
            best = [dx, dy]

    return [int(best[0]), int(best[1])]