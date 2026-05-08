def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        dist = abs(nx - ox) + abs(ny - oy)

        # Simple obstacle pressure: count immediate blocked neighbors to avoid dead-ends (deterministic).
        neigh = 0
        for ddx, ddy in moves:
            if ddx == 0 and ddy == 0:
                continue
            tx, ty = nx + ddx, ny + ddy
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
                neigh += 1

        res_term = 0
        if resources:
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            res_term = -0.1 * dres if is_pursuer else -0.05 * dres

        corner_term = 0
        if is_pursuer:
            # Close towards opponent while also biasing to reduce distance to opposite corner (helps wall-running corner squeeze).
            corner_term = -0.02 * (abs(nx - near_corner[0]) + abs(ny - near_corner[1]))
        else:
            corner_term = 0.02 * (abs(nx - far_corner[0]) + abs(ny - far_corner[1]))

        # Higher is better.
        if is_pursuer:
            score = (-dist) - 0.08 * neigh + res_term + corner_term
        else:
            score = (dist) - 0.06 * neigh + res_term + corner_term

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]