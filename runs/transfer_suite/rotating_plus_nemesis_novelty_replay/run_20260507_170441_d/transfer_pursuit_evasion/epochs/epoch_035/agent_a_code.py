def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if (sx, sy) == (ox, oy):
        return [0, 0]

    best_move = (0, 0)
    best_val = 10**18

    for mdx, mdy in dirs:
        nsx, nsy = sx + mdx, sy + mdy
        if not ok(nsx, nsy):
            nsx, nsy = sx, sy  # engine would keep us in place
        if (nsx, nsy) == (ox, oy):
            return [mdx, mdy]

        # Opponent maximizes distance from our next position
        best_op_dist = -1
        best_op = (0, 0)
        for odx, ody in dirs:
            nosx, nosy = ox + odx, oy + ody
            if not ok(nosx, nosy):
                nosx, nosy = ox, oy
            d = man(nsx, nsy, nosx, nosy)
            if d > best_op_dist:
                best_op_dist = d
                best_op = (odx, ody)

        # We minimize the opponent's best-case distance
        if best_op_dist < best_val:
            best_val = best_op_dist
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]