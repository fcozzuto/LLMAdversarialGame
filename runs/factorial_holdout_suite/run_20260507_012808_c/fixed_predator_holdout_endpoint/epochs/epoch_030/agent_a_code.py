def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    if not resources or (sx, sy) in set(resources):
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def key_adv(res):
        rx, ry = res
        myd = md(rx, ry, sx, sy)
        opd = md(rx, ry, ox, oy)
        return (opd - myd, -myd, -rx, -ry)

    better = []
    for r in resources:
        if md(r[0], r[1], sx, sy) < md(r[0], r[1], ox, oy):
            better.append(r)

    if better:
        target = max(better, key=key_adv)
    else:
        target = min(resources, key=lambda r: (md(r[0], r[1], ox, oy), md(r[0], r[1], sx, sy), r[0], r[1]))

    tx, ty = target

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = md(tx, ty, nx, ny)
        opd2 = md(tx, ty, ox, oy)
        opp_pressure = -opd2  # constant across our moves, but keeps structure stable
        eval_key = (myd2, opp_pressure, dx == 0 and dy == 0, tx, ty, nx, ny)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]