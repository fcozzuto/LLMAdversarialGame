def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Midline "pressure": favor staying near the line between corners (diagonal mid).
    midx = (w - 1) / 2.0
    midy = (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        if resources:
            dmin_us = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            dmin_op = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            # competing on same target: prefer moves that make us no worse than opponent
            dmin_op_from_n = min(cheb(nx, ny, rx, ry) + cheb(ox, oy, rx, ry) for rx, ry in resources)
            # compare arrival advantage
            us_adv = min((cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)) for rx, ry in resources)
        else:
            dmin_us = 0
            dmin_op = 0
            us_adv = 0
            dmin_op_from_n = 0

        # Block/opponent distance shaping: increase distance from opponent slightly to avoid being chased,
        # but keep pressure by not retreating too much.
        d_opp = cheb(nx, ny, ox, oy)
        d_opp_now = cheb(sx, sy, ox, oy)

        # Favor moving toward midline if we can't secure resources quickly (obstacle-sensitive determinism).
        mid_pen = abs(nx - midx) + abs(ny - midy)

        val = 0
        # Main goal: minimize distance to resources strongly; if behind, shift to disruption via midline/opp distance.
        val += -12 * dmin_us
        val += -2 * mid_pen
        # If we can get a target earlier (us_adv <= 0), reward; otherwise penalize.
        val += (-6 * us_adv)
        # Disruption: if we're close to a resource, still try to make opponent farther in relative terms.
        if resources:
            val += 3 * (dmin_op - dmin_us)
        # Opponent interaction: avoid getting closer unless it improves target distance enough.
        val += 2 * (d_opp - d_opp_now)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]