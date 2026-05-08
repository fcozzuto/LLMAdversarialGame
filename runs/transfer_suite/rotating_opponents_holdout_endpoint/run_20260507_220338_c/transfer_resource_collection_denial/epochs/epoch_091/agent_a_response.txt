def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev (matches king-like moves)

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Evaluate each move by worst-case advantage across resources.
    # Want high (self_dist - opp_dist): larger means you are farther, which is bad for collecting first.
    # So instead maximize (opp_dist - self_dist), i.e., how much closer you are than opponent.
    best = None
    for dx, dy, nx, ny in legal:
        best_adv = -10**9
        best_self_closer = 10**9
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer
            if adv > best_adv or (adv == best_adv and sd < best_self_closer):
                best_adv = adv
                best_self_closer = sd
        # Favor moves that keep us from getting too far behind: secondary is maximum closeness score.
        # Deterministic tie-break: smaller dx, then smaller dy.
        cand = (best_adv, -best_self_closer, -abs(ox - nx) - abs(oy - ny), -dx, -dy, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[-2]), int(best[-1])]