def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res_cells.append((x, y))
    if not res_cells:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(res_cells)) or len(res_cells))
    endgame = 1.8 if rem <= 5 else 1.0

    best = None
    bestv = None
    for x, y in res_cells:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        adv = (od - sd)  # positive if we are closer
        # Prefer stealing/being closer, then quick pickup, with endgame urgency
        v = (adv * 12.0 * endgame) + (1.0 / (1 + sd)) + (0.02 * (w + h - sd))
        if bestv is None or v > bestv:
            bestv = v
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If target delta leads directly into obstacle, try alternative axis move
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        if (sx + dx, sy) not in obstacles and (sx + dx, sy) != (sx, sy):
            return [dx, 0]
        if (sx, sy + dy) not in obstacles and (sx, sy + dy) != (sx, sy):
            return [0, dy]
        # Fallback: choose one step minimizing distance to target among valid deltas
        candidates = []
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                cx, cy = sx + ddx, sy + ddy
                if (0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles):
                    dist = abs(tx - cx) + abs(ty - cy)
                    candidates.append((dist, abs(ddx) + abs(ddy), ddx, ddy))
        if candidates:
            candidates.sort()
            return [int(candidates[0][2]), int(candidates[0][3])]

    return [int(dx), int(dy)]