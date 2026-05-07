def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obst = observation.get("obstacles") or []
    obstacles = set()
    for p in obst:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Prefer routes where we are closer than opponent; break ties by being close to a resource.
            adv = od - sd
            score = adv * 1000 - sd
            if best_for_move is None or score > best_for_move:
                best_for_move = score

        if best_for_move is None:
            continue

        # Small deterministic tie-break: keep nearer to center.
        center_pen = int(abs(nx - cx) + abs(ny - cy))
        final_score = best_for_move - center_pen

        if best_score is None or final_score > best_score:
            best_score = final_score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]