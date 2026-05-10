def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: man(p[0], p[1], ox, oy))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
            if (sx + dx, sy) in obstacles or not inb(sx + dx, sy):
                dx = 0
            if (sx, sy + dy) in obstacles or not inb(sx, sy + dy):
                dy = 0
        return [dx, dy]

    best_target = None
    best_val = None
    for rx, ry in resources:
        d_self = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # Sweep-style opponents often contest by advancing across a row/col; penalize targets they can reach sooner.
        contest = 0
        if ry == oy or rx == ox:
            if d_opp <= d_self:
                contest = 3 + (d_self - d_opp)
        val = (d_self + contest, -d_opp, d_self)
        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    best_step = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Prefer getting closer to target while staying relatively far from opponent.
        # Slightly bias alignment with opponent row/col to counter sweep_rows harassment.
        align_pen = 0
        if ny == oy or nx == ox:
            align_pen = 1
        key = (d_self, align_pen, -(d_opp), dx, dy)
        if best_step is None or key < best_step[0]:
            best_step = (key, [dx, dy])

    if best_step is None:
        return [0, 0]
    return best_step[1]