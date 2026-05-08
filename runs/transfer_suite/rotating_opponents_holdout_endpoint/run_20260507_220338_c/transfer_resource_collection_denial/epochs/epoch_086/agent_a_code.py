def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                dirs.append((dx, dy))
    dirs = dirs if dirs else [(0, 0)]

    def dist_cheb(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax >= ay else ay

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        d_opp = dist_cheb(nx, ny, ox, oy)
        if resources:
            d_res = min(dist_cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_best = d_res
        else:
            d_best = dist_cheb(nx, ny, ox, oy)  # if no resources, move away from opponent
        score = (-d_best) + (0.15 * d_opp)
        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]