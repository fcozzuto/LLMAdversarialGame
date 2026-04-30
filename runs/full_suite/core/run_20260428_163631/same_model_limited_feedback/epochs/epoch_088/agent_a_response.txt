def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # If no resources, head toward center to avoid getting stuck near corners.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Pick resource where we are relatively closer than opponent.
        best = None
        for rx, ry in resources:
            my_d = abs(rx - sx) + abs(ry - sy)
            op_d = abs(rx - ox) + abs(ry - oy)
            # Prefer immediate capture, then maximize (opponent distance - ours), tie-break by coords.
            val = (op_d - my_d) + (1000 if my_d == 0 else 0)
            key = (val, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry), my_d, op_d)
        tx, ty = best[1]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    candidates = []
    # Deterministic move preference order: closer first, then prefer dx,dy toward target.
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            my_d = abs(tx - nx) + abs(ty - ny)
            # Small bias toward moving in correct direction.
            bias = 0
            if nx != tx:
                bias += 1 if (nx - tx) * dx <= 0 else 0
            if ny != ty:
                bias += 1 if (ny - ty) * dy <= 0 else 0
            candidates.append((my_d, -bias, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, best_dx, best_dy, _, _ = candidates[0]
    return [int(best_dx), int(best_dy)]