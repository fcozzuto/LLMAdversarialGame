def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def center_bias(x, y):
        dx = x - cx0
        dy = y - cy0
        return -(dx * dx + dy * dy) * 0.005

    def cell_pen(x, y):
        if (x, y) in obstacles:
            return -1000.0
        return 0.0

    # Choose best move by "race" scoring against opponent for each resource.
    best = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = cell_pen(nx, ny)
        if resources:
            myd = man(nx, ny, ox, oy)
            # Resource scoring: prioritize resources where we gain tempo vs opponent, then tie-break to closeness.
            s = 0.0
            for (rx, ry) in resources:
                if (rx, ry) in obstacles:
                    continue
                my = man(nx, ny, rx, ry)
                opp = man(ox, oy, rx, ry)
                gain = opp - my  # positive means we are closer
                # Encourage stealing and also landing near a resource.
                s += (gain * 8.0 + (18.0 - my) * 0.3) * (1.0 / (1 + my))
            # If no clear winning resource, fallback to reducing opponent distance to intercept.
            if len(resources) <= 2:
                s = s + (myd * -0.12)
            score = pen + s + center_bias(nx, ny)
        else:
            # No resources visible: move to intercept by approaching opponent and center.
            score = pen + center_bias(nx, ny) - man(nx, ny, ox, oy) * 0.15
        if score > best_score + 1e-9:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]