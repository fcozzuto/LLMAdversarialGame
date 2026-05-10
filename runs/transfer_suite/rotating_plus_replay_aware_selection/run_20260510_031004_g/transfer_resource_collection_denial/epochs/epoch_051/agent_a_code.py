def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = (-1, 0, 1)

    # If no resources, just stay.
    if not resources:
        return [0, 0]

    # Choose target deterministically: prioritize resources where we are closer than opponent.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better; tie-break by coordinates.
        score = (do - ds, -ds, -rx, -ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)

    if best is None:
        return [0, 0]

    _, tx, ty = best

    # Pick a valid move that reduces distance to target; if blocked, try other moves by same key.
    curd = cheb(sx, sy, tx, ty)
    candidates = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                nd = cheb(nx, ny, tx, ty)
                # Prefer strictly closer; then prefer also being ahead vs opponent for same target.
                n_do = cheb(ox, oy, tx, ty)
                key = (curd - nd, (n_do - nd), -abs((nx - tx)), -abs((ny - ty)), -dx, -dy)
                candidates.append((key, dx, dy))

    if candidates:
        candidates.sort(reverse=True)
        return [int(candidates[0][1]), int(candidates[0][2])]

    # If all progress moves are blocked, allow staying.
    return [0, 0]