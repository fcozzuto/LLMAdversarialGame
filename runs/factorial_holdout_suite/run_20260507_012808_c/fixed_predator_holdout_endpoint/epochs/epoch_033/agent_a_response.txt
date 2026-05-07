def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0, None)  # val, self_dist, move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Evaluate the best resource to target from (nx, ny)
        cell_best_val = None
        cell_best_selfd = None
        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Assume opponent moves too: give self_d a small disadvantage unless we are already closer
            rel = (opp_d - self_d)
            # Prefer resources where self is clearly ahead; also prefer shorter self_d when close
            val = rel * 10 - self_d
            # Tiny deterministic secondary: prefer resources with smaller coordinate sum
            val2 = val - (rx + ry) * 0.01
            if cell_best_val is None or val2 > cell_best_val or (val2 == cell_best_val and self_d < cell_best_selfd):
                cell_best_val = val2
                cell_best_selfd = self_d
        if cell_best_val is None:
            continue
        if (best[2] is None) or (cell_best_val > best[0]) or (cell_best_val == best[0] and cell_best_selfd < best[1]):
            best = (cell_best_val, cell_best_selfd, [dx, dy])

    return best[2] if best[2] is not None else [0, 0]