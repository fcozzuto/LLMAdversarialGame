def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def cell_key(cx, cy):
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        return (od - sd, -sd, -od, cx, cy)

    tx, ty = max(resources, key=lambda c: cell_key(c[0], c[1]))
    best = None
    best_key = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # If we're moving, keep priority: reach a cell that improves our advantage.
            sd2 = cheb(nx, ny, tx, ty)
            od2 = cheb(ox, oy, tx, ty)
            cur_adv = od2 - sd2
            # Small tie-break: avoid stepping into/adjacent to obstacles.
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx + ax, ny + ay
                    if inb(px, py) and (px, py) in obstacles:
                        adj_obs += 1
            k = (cur_adv, -sd2, -od2, -adj_obs, nx, ny)
            if best_key is None or k > best_key:
                best_key = k
                best = (dx if nx != sx else 0, dy if ny != sy else 0)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]