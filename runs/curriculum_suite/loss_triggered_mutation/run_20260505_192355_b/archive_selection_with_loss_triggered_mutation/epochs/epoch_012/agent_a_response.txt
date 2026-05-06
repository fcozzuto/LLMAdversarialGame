def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order
    moves = sorted(moves)

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Denier-style: after our move, pick target resource where we maximize (opd - myd)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # Find best contested target for this move
        local_best = None  # (primary, secondary, target_index)
        for i, (tx, ty) in enumerate(resources):
            myd = manh(nx, ny, tx, ty)
            opd = manh(ox, oy, tx, ty)
            # Primary: maximize distance advantage; Secondary: prefer smaller myd
            key = (-(opd - myd), myd, i)
            if local_best is None or key < local_best[0]:
                local_best = (key, (opd - myd, myd))
        if local_best is None:
            continue
        _, (adv, myd) = local_best
        # Score: prioritize denying (adv), then being close (myd), then slight bias toward board center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.0001
        score = (adv, -myd, center_bias)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]