def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rr = (int(r[0]), int(r[1]))
            if rr not in obstacles:
                resources.append(rr)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a resource that opponent likely targets, but we can potentially contest.
    best_target, best_key = None, None
    for tx, ty in resources:
        d_o = man(ox, oy, tx, ty)
        d_s = man(sx, sy, tx, ty)
        # Lower is better: opponent close, we not too far (to enable denial/intercept).
        key = (d_o - d_s, d_o, -((tx == 0 or tx == w - 1) or (ty == 0 or ty == h - 1)))
        if best_key is None or key < best_key:
            best_key, best_target = key, (tx, ty)

    tx, ty = best_target
    my_want = 1
    opp_want = 2
    center_bias = 0.5

    best_move, best_val = (0, 0), None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps us if invalid
            dx, dy = 0, 0
        d_my = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Evaluate after move: go closer to target while pushing opponent farther in relative terms.
        # Also slightly bias toward board center to reduce boundary trapping.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)

        val = (d_my * my_want) + (-(d_opp - d_my) * opp_want) + dist_center * center_bias

        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]