def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    free_targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                free_targets.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_key = None
    for tx, ty in free_targets:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer targets where we are relatively closer than opponent.
        key = (-(od - sd), sd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if best_target is None:
        # No valid resource; move toward center deterministically.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                candidates.append((cheb(nx, ny, cx, cy), nx, ny))
        candidates.sort()
        _, nx, ny = candidates[0] if candidates else (0, sx, sy)
        return [nx - sx, ny - sy]

    tx, ty = best_target
    sd0 = cheb(sx, sy, tx, ty)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        # Primary: reduce self distance; secondary: maximize progress advantage.
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        key = (-adv, sd, abs(nx - ox) + abs(ny - oy), nx, ny)
        candidates.append((key, sd0 - sd, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, nx, ny = candidates[0]
    return [nx - sx, ny - sy]