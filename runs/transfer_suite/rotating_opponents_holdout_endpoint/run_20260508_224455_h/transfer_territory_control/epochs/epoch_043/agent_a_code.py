def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        if c is None:
            continue
        obstacles.add((int(c[0]), int(c[1])))

    resources = []
    for c in (observation.get("resources", []) or []):
        if c is None:
            continue
        resources.append((int(c[0]), int(c[1])))

    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def best_resource_cell(x, y):
        if not resources:
            return None
        bx, by = resources[0]
        bd = dist(x, y, bx, by)
        for r in resources[1:]:
            rr_x, rr_y = r
            d = dist(x, y, rr_x, rr_y)
            if d < bd:
                bd, bx, by = d, rr_x, rr_y
        return bx, by

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            rxry = best_resource_cell(nx, ny)
            rx, ry = rxry
            res_d = dist(nx, ny, rx, ry)
        else:
            res_d = dist(nx, ny, cx, cy)
        opp_d = dist(nx, ny, ox, oy)
        val = (-res_d) + (opp_d * 0.001) + (1 if (nx, ny) in unclaimed else 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move in ([d[0], d[1]] for d in dirs) else [0, 0]