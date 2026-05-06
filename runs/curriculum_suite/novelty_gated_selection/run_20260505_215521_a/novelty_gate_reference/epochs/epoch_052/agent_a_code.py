def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                v = (0, abs(nx - ox) + abs(ny - oy), abs(ny - oy))
                if best is None or v < best[0] or (v == best[0] and (nx, ny) < best[1]):
                    best = (v, (nx, ny), (dx, dy))
        return [best[2][0], best[2][1]] if best else [0, 0]

    # Target selection: seek resources where we can arrive meaningfully earlier,
    # and prefer shifting away from opponent's row if they are aligned.
    opp_row_pressure = 1 if sy == oy else 0
    best_t = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        advantage = od - sd  # higher is better
        row_bias = abs(ty - oy)  # prefer farther row from opponent sweep
        penalty = opp_row_pressure * (-1 if ty == oy else 0)  # avoid same row when aligned
        key = (-advantage, sd, -row_bias + penalty, tx, ty)  # lex-deterministic
        if best_t is None or key < best_t[0]:
            best_t = (key, (tx, ty), sd, od)

    tx, ty = best_t[1]

    # Move choice: choose valid step minimizing distance to target, but if opponent is on same row,
    # discourage staying on that row to counter "sweep_rows".
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        row_pen = (sy == oy and ny == oy)  # stay on opponent row is bad when aligned
        opp_d = cheb(nx, ny, ox, oy)
        key = (d, row_pen, opp_d, abs(nx - sx) + abs(ny - sy), nx, ny)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]] if best else [0, 0]