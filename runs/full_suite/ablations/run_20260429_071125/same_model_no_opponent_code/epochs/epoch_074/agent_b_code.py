def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def nearest(tx, ty):
        if not resources:
            return tx, ty
        best = None
        for x, y in resources:
            d = man(tx, ty, x, y)
            if best is None or d < best[0] or (d == best[0] and (x < best[1] or (x == best[1] and y < best[2]))):
                best = (d, x, y)
        return best[1], best[2]

    my_tx, my_ty = nearest(sx, sy)
    op_tx, op_ty = nearest(ox, oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        v = 0
        v += -man(nx, ny, my_tx, my_ty)
        v += -0.6 * man(nx, ny, op_tx, op_ty)
        v += -0.05 * man(nx, ny, ox, oy)  # slight separation
        # prefer moves that land on a resource
        if (nx, ny) in resources:
            v += 5.0
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]