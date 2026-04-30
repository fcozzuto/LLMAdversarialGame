def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manh(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    def nearest_res_dist(x, y):
        if not resources:
            return manh(x, y, ox, oy)
        best = 10**9
        for rx, ry in resources:
            d = manh(x, y, rx, ry)
            if d < best:
                best = d
        return best

    def score(x, y):
        nr = nearest_res_dist(x, y)  # smaller is better
        dop = manh(x, y, ox, oy)    # larger is better
        return (nr, -dop)

    # Tie-breakers: prefer moving that improves next-step resource distance and keeps away from opponent.
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s1 = score(nx, ny)
        # one-step lookahead: assume we can choose our next best, approximate by our best possible move from (nx, ny)
        la_best = 10**9
        la_dop = 0
        for ddx, ddy in moves:
            nnx, nny = nx + ddx, ny + ddy
            if not valid(nnx, nny):
                continue
            ns = score(nnx, nny)
            # ns = (nearest, -dop); compare primarily nearest, then dop
            if ns[0] < la_best:
                la_best = ns[0]
                la_dop = -ns[1]
            elif ns[0] == la_best and (-ns[1]) > la_dop:
                la_dop = -ns[1]
        key = (s1[0], -s1[1], la_best, la_dop, -abs(nx - (w // 2)) - abs(ny - (h // 2)), dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]