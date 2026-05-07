def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        cur_best = None
        for rx, ry in resources[:20]:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            val = od - sd
            if cur_best is None or val > cur_best[0] or (val == cur_best[0] and sd < cur_best[1]) or (val == cur_best[0] and sd == cur_best[1] and (rx, ry) < cur_best[2]):
                cur_best = (val, sd, (rx, ry))
        if cur_best is None:
            continue
        if best is None or cur_best[0] > best[0] or (cur_best[0] == best[0] and cur_best[1] < best[1]) or (cur_best[0] == best[0] and cur_best[1] == best[1] and dx, dy < best[2]):
            best = (cur_best[0], cur_best[1], (dx, dy))
    if best is None:
        return [0, 0]
    return [best[2][0], best[2][1]]