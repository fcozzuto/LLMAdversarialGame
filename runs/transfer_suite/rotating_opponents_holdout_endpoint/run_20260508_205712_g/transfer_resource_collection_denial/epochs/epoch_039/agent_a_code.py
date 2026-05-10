def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    best_move = (0, 0)
    best_key = None

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            k = (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty), -free_neighbors(nx, ny), -nx, -ny)
            if best_key is None or k > best_key:
                best_key = k
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Evaluate each possible move by its best achievable resource advantage next step.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Max over resources of (opponent_distance - self_distance), with tiebreakers.
        best_for_cell = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # Prefer immediate/earlier capture (sd small) and avoid far targets.
            k = (adv, -sd, -cheb(sx, sy, rx, ry), -rx - ry)
            if best_for_cell is None or k > best_for_cell:
                best_for_cell = k

        # If we can't gain advantage, still pick the cell that minimizes our distance to the closest resource.
        if best_for_cell is None:
            continue

        # Cell-level tie-breakers: mobility and obstacle pressure.
        cell_key = (best_for_cell[0], best_for_cell[1], best_for_cell[2], best_for_cell[3], free_neighbors(nx, ny), -nx, -ny)
        if best_key is None or cell_key > best_key:
            best_key = cell_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]