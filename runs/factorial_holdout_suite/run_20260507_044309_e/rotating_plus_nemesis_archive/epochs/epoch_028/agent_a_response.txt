def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]
    # Deterministic tie-breaking order: prefer diagonal toward increasing x then increasing y
    dirs.sort(key=lambda d: (-(d[0] == 1), -(d[1] == 1), d[0], d[1]))

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy

        # Evaluate move by best available resource we can "win" soonest, with small preference for row/column progress.
        my_best = None
        for tx, ty in resources:
            d_my = cheb((nx, ny), (tx, ty))
            d_op = cheb((ox, oy), (tx, ty))
            # win score: strictly earlier is best; if tie, favor larger distance lead for opponent; otherwise favor nearer target.
            lead = d_op - d_my
            key = (1 if d_my < d_op else 0 if d_my == d_op else -1, lead, -d_my, -(tx + ty))
            if my_best is None or key > my_best[0]:
                my_best = (key, (tx, ty), d_my)

        k, (tx, ty), d_my = my_best
        # Extra heuristic vs sweep_rows: discourage overcommitting to same row if opponent is much closer on that row.
        row_pen = 0
        if ox != sx:
            # compare closeness to resources in our target row vs opponent closeness
            my_row = abs(ty - ny)
            op_row = abs(ty - oy)
            if op_row < my_row and cheb((ox, oy), (tx, ty)) <= cheb((nx, ny), (tx, ty)):
                row_pen = 1

        val = (k[0], k[1], k[2], -abs(tx - nx), -abs(ty - ny), -(d_my + row_pen))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [nx - sx, ny - sy]

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]