def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose move that maximizes (opponent advantage vs our advantage) while also moving toward target.
    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate best resource from this next position
        best_for_move = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent; then prefer smallest our distance.
            adv = od - sd  # higher is better for us
            # Small tie-break discourages being stuck: prefer progress in combined direction to target.
            progress = -(abs(nx - rx) + abs(ny - ry))
            key = (adv, -sd, progress, rx, ry)
            if best_for_move is None or key > best_for_move[0]:
                best_for_move = (key, (rx, ry))
        # Primary: best_for_move quality; Secondary: minimize our distance to that resource; then deterministic order.
        k = best_for_move[0]
        move_key = (k[0], k[1], k[2], abs(nx - rx if best_for_move else nx) + abs(ny - ry if best_for_move else ny), dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = [dx, dy]

    return best_move if best_move else [0, 0]