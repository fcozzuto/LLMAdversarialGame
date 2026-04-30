def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_move_toward(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                nx, ny = sx, sy
                dx, dy = 0, 0
            ns = cheb(nx, ny, tx, ty)
            no = cheb(ox, oy, tx, ty)
            # Prefer positions that improve relative closeness vs opponent.
            key = (ns - no, ns, cheb(nx, ny, (w - 1) // 2, (h - 1) // 2), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return best[1]

    if resources:
        # Pick a resource where we're relatively closer than opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_res = None
        for rx, ry in resources:
            selfd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Tie-break by favoring central resources and shorter absolute distance.
            key = (selfd - oppd, selfd, cheb(rx, ry, cx, cy))
            if best_res is None or key < best_res[0]:
                best_res = (key, (rx, ry))
        rx, ry = best_res[1]
        return [best_move_toward(rx, ry)[0], best_move_toward(rx, ry)[1]]

    # No resources: go toward center while avoiding obstacles deterministically.
    target_x, target_y = (w - 1) // 2, (h - 1) // 2
    mv = best_move_toward(target_x, target_y)
    return [mv[0], mv[1]]