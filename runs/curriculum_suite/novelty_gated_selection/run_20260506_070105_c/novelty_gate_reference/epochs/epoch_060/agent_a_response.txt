def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2
    best = None

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Relative targeting: pick move that most reduces (our_dist - opp_dist) to any resource
            best_rel = None
            best_our = None
            for rx, ry in resources:
                our_d = abs(nx - rx) + abs(ny - ry)
                opp_d = abs(nx - ox) + abs(ny - oy)
                rel = our_d - opp_d
                if best_rel is None or rel < best_rel or (rel == best_rel and our_d < best_our):
                    best_rel = rel
                    best_our = our_d
            # Tie-breakers: prefer fewer our steps, then closer to center (deterministic)
            key = (best_rel, best_our, abs(nx - cx) + abs(ny - cy), nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # No resources: go toward center while keeping distance from opponent
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        key = (abs(nx - cx) + abs(ny - cy), -(abs(nx - ox) + abs(ny - oy)), nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]] if best else [0, 0]