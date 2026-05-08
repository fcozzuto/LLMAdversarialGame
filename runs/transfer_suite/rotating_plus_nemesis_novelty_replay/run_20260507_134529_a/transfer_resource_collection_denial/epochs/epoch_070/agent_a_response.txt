def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w, h = observation["grid_width"], observation["grid_height"]

    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = max(abs(nx - ox), abs(ny - oy))
            if v > best[0] or (v == best[0] and (nx, ny) < (best[1], best[2])):
                best = (v, nx, ny)
        return [best[1] - sx, best[2] - sy]

    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    best_move = (0, 0)
    best_val = (-10**18, 10**9, 10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        myd = man(nx, ny, tx, ty)
        myd2 = myd
        op_choose = (man(ox, oy, tx, ty) - myd)  # approximate denial
        # also consider immediate "grab": if we're at resource, prioritize
        on_resource = 1 if (nx, ny) == (tx, ty) else 0

        # secondary: prevent giving opponent closer access to our best target
        oppd = man(ox, oy, tx, ty)
        val = (op_choose + 2 * on_resource, -myd2, -oppd, on_resource)
        # deterministic tie by lexicographic move preference
        move_key = (val, nx, ny)
        if best_move == (0, 0) and best_val == (-10**18, 10**9, 10**9):
            best_val = val
            best_move = (dx if free(sx + dx, sy + dy) else 0, dy if free(sx + dx, sy + dy) else 0)
        else:
            if val > best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
                best_val = val
                best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]