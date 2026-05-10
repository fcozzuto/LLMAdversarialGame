def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    env = observation.get("environment_name", "resource_collection")

    if env != "resource_collection":
        # Fallback: go to center
        tx, ty = w // 2, h // 2
        best = [0, 0]
        best_key = (10**9, 10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d = abs(tx - nx) + abs(ty - ny)
                key = (d, abs(dx) + abs(dy), dx, dy)
                if key < best_key:
                    best_key = key
                    best = [dx, dy]
        return best

    # Targeting heuristic: prefer resources where we are closer (or can become closer) than opponent.
    if resources:
        best_target = None
        best_key = None
        for rx, ry in resources:
            md = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            key = (-1 if od == 0 else 0, -(md == 0), (md - od), md, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)
        tx, ty = best_target
    else:
        tx, ty = w // 2, h // 2

    # Evaluate candidate moves.
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            myd = abs(tx - nx) + abs(ty - ny)
            opd = abs(tx - (ox + dx)) + abs(ty - (oy + dy))

            # If resource exists at next cell, strongly prefer.
            at_resource = 1 if (tx == nx and ty == ny) else 0

            # Also consider if this move reduces our distance and/or increases opponent distance.
            delta_my = (abs(tx - sx) + abs(ty - sy)) - myd
            delta_op = opd - (abs(tx - ox) + abs(ty - oy))

            # Prefer not to waste steps: small penalty for staying, deterministic tie-break.
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            score = (
                -at_resource,
                myd,
                -opd + (0.0 if at_resource else 0.0),
                -delta_my,
                delta_op,
                stay_pen,
                abs(dx) + abs(dy),
                dx,
                dy,
            )
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]