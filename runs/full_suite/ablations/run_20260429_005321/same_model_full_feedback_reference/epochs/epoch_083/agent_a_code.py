def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)  # maximize distance if no resources
            if best_val is None or v > best_val or (v == best_val and (dx, dy) < best):
                best_val, best = v, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    res_set = set(resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_best = -10**18
        for rx, ry in resources:
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            val = opd - myd
            if (nx, ny) == (rx, ry):
                val += 10**9
            if val > my_best:
                my_best = val
        # Tie-break deterministically: prefer closer to the same best target (lower myd), then lower dx,dy
        if best_val is None or my_best > best_val:
            best_val, best = my_best, (dx, dy)
        elif my_best == best_val:
            if (dx, dy) < best:
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]