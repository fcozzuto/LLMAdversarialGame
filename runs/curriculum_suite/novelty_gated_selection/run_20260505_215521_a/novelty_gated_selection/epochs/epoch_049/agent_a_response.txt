def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if w <= 0 or h <= 0:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    opp_close = abs(sx - ox) + abs(sy - oy)
    res_count = int(observation.get("remaining_resource_count", 0) or 0)
    # If few resources left, be more aggressive about racing for a head-start.
    ahead_weight = 6.0 if res_count <= 4 else 4.0
    dist_weight = 1.2 if res_count <= 4 else 0.9
    avoid_weight = 5.0 if opp_close <= 3 else 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        if resources:
            # Race for a resource where we are relatively closer than the opponent.
            best_ahead = 10**9
            best_res_d = 10**9
            for rx, ry in resources:
                myd = abs(nx - rx) + abs(ny - ry)
                opd = abs(ox - rx) + abs(oy - ry)
                ahead = myd - opd  # negative means we are closer
                if ahead < best_ahead or (ahead == best_ahead and myd < best_res_d):
                    best_ahead = ahead
                    best_res_d = myd
            # Evaluate move: prefer smaller ahead, then closer to that resource.
            val = -ahead_weight * best_ahead - dist_weight * best_res_d
        else:
            # No resources: drift toward center deterministically.
            cx, cy = w // 2, h // 2
            val = -abs(nx - cx) - abs(ny - cy)

        # Safety: discourage moves that get too close to opponent.
        ndop = abs(nx - ox) + abs(ny - oy)
        val -= avoid_weight * max(0, 3 - ndop)  # penalty when within 2 steps (Manhattan)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]