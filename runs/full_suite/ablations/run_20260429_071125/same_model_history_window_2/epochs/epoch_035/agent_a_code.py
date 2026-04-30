def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    rc = observation.get("remaining_resource_count", None)
    try:
        rc = int(rc)
    except:
        rc = len(resources)
    low_left = 1 if rc <= 4 else 0

    # Select target with a decisive change: prioritize resources we can "win" (we <= opponent distance),
    # otherwise pick the safest (maximizing opponent delay) based on a combined score.
    best = None
    best_key = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        win = 1 if ds <= do else 0
        # If few resources left, push harder to steal/close; otherwise focus on reducing opponent advantage.
        if low_left:
            key = (0 if win else 1, ds - do, ds, x, y)
        else:
            key = (0 if win else 1, (ds - do) + (0 if win else 3), ds, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    # Move choice: minimize distance to target; secondarily minimize proximity to opponent; tie-break deterministically.
    best_move = None
    best_move_key = None
    for dx, dy, nx, ny in valid:
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(nx, ny, ox, oy)
        # When low_left, also avoid giving opponent a quick path to the same target.
        give_pen = 0 if low_left == 0 else (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty))
        key = (d1, d2, give_pen, nx, ny, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]