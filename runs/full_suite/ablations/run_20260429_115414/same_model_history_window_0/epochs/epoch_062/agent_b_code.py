def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # If no resources, head toward opponent corner deterministically
    if not resources:
        tx, ty = (w - 1, h - 1) if (sx, sy) == (0, 0) else (0, 0)
        target = (tx, ty)
    else:
        best = None
        best_key = None
        for r in resources:
            rx, ry = r
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Prefer resources we are closer to; small tie-break toward lower x,y
            key = (sd - od * 0.9, sd, rx, ry)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        target = best

    tx, ty = target
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            # Tie-break deterministically: prefer fewer moves, then lexicographic dx,dy
            move_cost = (0 if (dx == 0 and dy == 0) else 1)
            candidates.append((d, move_cost, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]