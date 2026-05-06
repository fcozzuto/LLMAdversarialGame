def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def key_for(r):
        rx, ry = r
        my_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        share_row = 1.0 if ry == oy else 0.0
        return (opp_d - my_d) + 0.4 * share_row, -my_d, -rx, -ry

    target = None
    bestk = None
    for r in resources:
        k = key_for(r)
        if bestk is None or k > bestk:
            bestk = k
            target = (r[0], r[1])

    tx, ty = target
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer moving closer; slight repulsion from opponent if it doesn't lose priority.
            d_now = man(sx, sy, ox, oy)
            d_new = man(nx, ny, ox, oy)
            dist_to_target = man(nx, ny, tx, ty)
            closer = man(sx, sy, tx, ty) - dist_to_target
            opp_pen = 0.08 * (d_now - d_new)  # move away if possible
            # If target lies on opponent's row, add contention caution.
            contend = 0.15 if ty == oy else 0.0
            score = (10 * closer) - dist_to_target - opp_pen - contend * (1 if man(nx, ny, ox, oy) < man(sx, sy, ox, oy) else 0)
            cand.append((score, dx, dy))

    cand.sort(reverse=True, key=lambda t: t[0])
    return [cand[0][1], cand[0][2]] if cand else [0, 0]