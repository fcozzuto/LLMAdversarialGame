def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_d(x, y):
        if not resources:
            return 0
        return min(man(x, y, rx, ry) for (rx, ry) in resources)

    op_best = best_d(ox, oy)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dres = best_d(nx, ny)
        on_res = 1 if any(nx == rx and ny == ry for (rx, ry) in resources) else 0
        dopp = man(nx, ny, ox, oy)
        v = 0
        v += on_res * 2000
        v += -(dres * 40)
        v += dopp * 3
        if resources:
            if dres + 0 < op_best:
                v += 250
            else:
                v -= 60
        if (nx == sx and ny == sy):
            v -= 5
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]