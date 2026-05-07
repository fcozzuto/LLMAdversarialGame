def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    best_moves = []
    best_score = -10**18

    # If we can grab a resource immediately, do so (deterministic tie by move order).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    # Otherwise, pick move that maximizes "opponent reach advantage" to some resource.
    if res_list:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Prefer resources we are closer to than opponent, weighted by how much.
            local_best = -10**18
            for rx, ry in res_list:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Larger (opd - myd) means we can arrive earlier.
                score = (opd - myd) * 1000 - myd
                if score > local_best:
                    local_best = score
            # Small tie-break: prefer smaller my distance to any resource.
            if local_best > best_score:
                best_score = local_best
                best_moves = [(dx, dy)]
            elif local_best == best_score:
                best_moves.append((dx, dy))
        # Deterministic: earliest in dirs order among best_moves.
        for dx, dy in dirs:
            if (dx, dy) in best_moves:
                return [dx, dy]

    # Fallback: minimize distance to nearest resource (or to opponent if none).
    target_x, target_y = (ox, oy) if not res_list else res_list[0]
    if res_list:
        best_m = None; best_d = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            mind = 10**9
            for rx, ry in res_list:
                d = cheb(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            if best_d is None or mind < best_d:
                best_d = mind; best_m = [dx, dy]
        return best_m if best_m is not None else [0, 0]

    best_d = None; best_m = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, target_x, target_y)
        if best_d is None or d < best_d:
            best_d = d; best_m = [dx, dy]
    return best_m