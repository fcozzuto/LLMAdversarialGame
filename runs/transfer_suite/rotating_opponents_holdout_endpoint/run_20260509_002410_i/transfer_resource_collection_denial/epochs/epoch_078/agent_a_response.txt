def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    cand = []
    for r in resources:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                dx1 = abs(sx - x); dy1 = abs(sy - y)
                my_d = dx1 if dx1 > dy1 else dy1
                dx2 = abs(ox - x); dy2 = abs(oy - y)
                op_d = dx2 if dx2 > dy2 else dy2
                lead = op_d - my_d  # positive: I’m closer
                tr = int(observation.get("turns_remaining", 0))
                parity_bias = 0.15 if ((tr + my_d) % 2 == 0) else -0.15
                # If I’m not leading, strongly prefer resources that still keep lead near 0 (avoid far behind)
                score = (lead + parity_bias) - (0.02 * my_d)
                cand.append((score, x, y, my_d, op_d))

    if not cand:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    prefer_close_when_low_turns = (tr < 30)

    cand.sort(key=lambda t: (
        -t[0],
        (t[3] if prefer_close_when_low_turns else t[4]),
        t[1], t[2]
    ))
    _, tx, ty, my_d, op_d = cand[0]

    ddx = tx - sx
    ddy = ty - sy
    step_x = 0 if ddx == 0 else (1 if ddx > 0 else -1)
    step_y = 0 if ddy == 0 else (1 if ddy > 0 else -1)

    # If staying on the exact step would not improve (blocked by obstacle), try axis-only alternatives deterministically
    nx = sx + step_x; ny = sy + step_y
    if (nx, ny) in obstacles:
        ax = (0 if ddx == 0 else (1 if ddx > 0 else -1))
        ay = (0 if ddy == 0 else (1 if ddy > 0 else -1))
        options = []
        if ax != 0:
            options.append((ax, 0))
        if ay != 0:
            options.append((0, ay))
        options.append((0, 0))
        for dxm, dym in options:
            xx = sx + dxm; yy = sy + dym
            if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in obstacles:
                return [int(dxm), int(dym)]
        return [0, 0]

    return [int(step_x), int(step_y)]