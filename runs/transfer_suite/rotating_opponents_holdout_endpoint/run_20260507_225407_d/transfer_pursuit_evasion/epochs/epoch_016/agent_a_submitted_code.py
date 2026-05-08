def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if r is None:
            continue
        if isinstance(r, dict):
            x = r.get("position") or (r.get("x"), r.get("y"))
            if isinstance(x, (list, tuple)) and len(x) >= 2:
                rx, ry = x[0], x[1]
            else:
                rx, ry = r.get("x"), r.get("y")
        else:
            rx, ry = r
        if rx is None or ry is None:
            continue
        rx, ry = int(rx), int(ry)
        if valid(rx, ry):
            res_list.append((rx, ry))

    if res_list:
        best = None
        bx = -10**18
        cx, cy = w / 2.0, h / 2.0
        for dx, dy, nx, ny in moves:
            mdx = abs(nx - sx) + abs(ny - sy)
            opp_bias = 0
            cur = -1
            for rx, ry in res_list:
                my_d = abs(nx - rx) + abs(ny - ry)
                opp_d = abs(ox - rx) + abs(oy - ry)
                s = (opp_d - my_d) - 0.05 * mdx + 0.001 * (abs(ox - rx) + abs(oy - ry))
                if s > cur:
                    cur = s
                    opp_bias = opp_d
            tie = - (abs(nx - cx) + abs(ny - cy))
            score = cur + 0.0001 * opp_bias + 0.00001 * tie
            if score > bx:
                bx = score
                best = [dx, dy]
        return best if best is not None else [0, 0]

    best = None
    bx = -10**18
    cx, cy = w / 2.0, h / 2.0
    for dx, dy, nx, ny in