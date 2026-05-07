def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Targeting: maximize advantage, but avoid sharing opponent's current row (sweep_rows pressure).
    best_t = None
    best_key = None
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        row_bias = 1.0 if ty != oy else -0.6
        # Prefer more advantageous targets; deterministic tie-breaks.
        key = (od - sd + row_bias, -sd, -tx, -ty, (ty - sy))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Move selection: maximize post-move advantage; prefer reducing self distance.
    best_move = [0, 0]
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            sd2 = cheb(nx, ny, tx, ty)
            od2 = cheb(ox, oy, tx, ty)
            # If we are closer, prioritize it; if we can deny (increase opponent distance gap), prioritize too.
            key = (od2 - sd2, -sd2, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]