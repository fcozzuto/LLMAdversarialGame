def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_move = (0, 0)
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        stayed = False
        if not valid(nx, ny):
            nx, ny = sx, sy
            stayed = True

        # Evaluate: maximize advantage of reaching some resource before opponent
        best_adv = -10**9
        best_self_d = 10**9
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer (or they are farther)
            if adv > best_adv or (adv == best_adv and sd < best_self_d):
                best_adv = adv
                best_self_d = sd

        # Prefer moving (not staying due to obstacle) when tie
        cand = (best_adv, -best_self_d, - (1 if stayed else 0), -(abs(dx) + abs(dy)))
        if best is None or cand > best:
            best = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]