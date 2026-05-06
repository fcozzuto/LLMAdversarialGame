def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        opp_target = min(resources, key=lambda t: man(ox, oy, t[0], t[1]))
    else:
        opp_target = (sx, sy)

    # Aim: deny opponent's nearest resource while still making progress if contest is weak.
    opp_to_target = man(ox, oy, opp_target[0], opp_target[1])
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    for dx, dy, nx, ny in moves:
        if resources:
            my_near = min(man(nx, ny, rx, ry) for rx, ry in resources)
        else:
            my_near = 10**9
        my_to_target = man(nx, ny, opp_target[0], opp_target[1])
        # Positive pressure when we can match/exceed opponent contest.
        contest = my_to_target - opp_to_target
        # Small tie-breakers: prefer better resource proximity and slight center control.
        center_bias = man(nx, ny, center_x, center_y)
        key = (contest, my_near, center_bias, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]