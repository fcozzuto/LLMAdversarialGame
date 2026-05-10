def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target that we can reach sooner (tie-break also considers opponent)
    best_key = None
    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer being ahead; if tied, prefer largest opponent disadvantage; then closer
        ahead = do - ds
        key = (ahead, -ds, -cheb(ox, oy, rx, ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Evaluate all legal moves; choose best improvement vs target with deterministic tie-break
    cur_ds = cheb(sx, sy, tx, ty)
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue

            ns_ds = cheb(nx, ny, tx, ty)
            ns_do = cheb(ox, oy, tx, ty)
            # Want to reduce our distance; also prefer moves that keep us ahead (or create lead)
            delta = cur_ds - ns_ds
            lead = ns_do - ns_ds
            # Soft preference: move direction that progresses; deterministic ordering by coordinates
            dist_to_target = ns_ds
            score = (delta, lead, -dist_to_target, -abs(dx), -abs(dy), -nx, -ny)
            cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]