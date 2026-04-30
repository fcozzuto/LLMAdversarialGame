def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    blocked = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        if (x, y) in blocked:
            return 10**9
        pen = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                pen += 10**9
            elif d == 1:
                pen += 150
            elif d == 2:
                pen += 20
        return pen

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_targets = []  # (score, rx, ry)
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we gain distance advantage; slight bias to closer ones.
        tscore = (od - sd) * 120 - sd * 3
        # Mild penalty if resource near obstacles to avoid detours.
        tpen = 0
        for ax, ay in obstacles:
            d = cheb(rx, ry, ax, ay)
            if d == 0:
                tpen += 10**6
            elif d == 1:
                tpen += 60
            elif d == 2:
                tpen += 10
        tscore -= tpen
        best_targets.append((tscore, rx, ry))
    if not best_targets:
        return [0, 0]
    best_targets.sort(key=lambda x: (-x[0], x[1], x[2]))
    best_targets = best_targets[:3]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = obst_pen(nx, ny)
        if pen >= 10**8:
            continue

        # Evaluate move against chosen top targets.
        # Aim to reduce our distance to the target while increasing opponent's distance.
        val = -pen
        for _, rx, ry in best_targets:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Bigger is better: we want d_self small and d_opp large.
            val += (d_opp - d_self) * 120 - d_self * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]