def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_key = None

    d_ov = abs(sx - ox) + abs(sy - oy)
    d_tc = abs(sx - tx) + abs(sy - ty)
    op_corner_dist = abs(ox - tx) + abs(oy - ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d2 = abs(nx - ox) + abs(ny - oy)
        dc = abs(nx - tx) + abs(ny - ty)

        # Containment: prefer moves that get us closer to their corner than they are,
        # and reduce distance along the escape axis to that corner.
        better_than_op = 1 if (dc < op_corner_dist) else 0
        axis = 0
        if tx != ox or ty != oy:
            axis = (0 if (dx == 0 and (tx == sx or ny == sy)) else 0)
        # Lexicographic-ish key: primarily close the gap; then reduce corner distance;
        # then ensure we are "in front" of the opponent relative to the corner.
        key = (
            d2,
            dc,
            -better_than_op,
            abs((nx - tx) - (ox - tx)) + abs((ny - ty) - (oy - ty)),
            abs(dx) + abs(dy),
        )

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]