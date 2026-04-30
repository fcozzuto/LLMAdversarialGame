def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = dirs[0]
    best_score = -10**9

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        if resources:
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            res_gain = (d_opp - d_self) * 10
        else:
            d_self = 0
            res_gain = 0

        d_foe = cheb(nx, ny, ox, oy)
        repulse = d_foe * 2

        near_obst = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in obst:
                    near_obst += 1

        score = res_gain + repulse - near_obst * 3
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if isinstance(best_move, tuple):
        best_move = list(best_move)
    if best_move == dirs[0] and (sx + best_move[0], sy + best_move[1]) in obst:
        return [0, 0]
    return best_move