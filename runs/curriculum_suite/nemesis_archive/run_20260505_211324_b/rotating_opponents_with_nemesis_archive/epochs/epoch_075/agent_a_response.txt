def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    center = ((w - 1) // 2, (h - 1) // 2)
    no_res = (len(resources) == 0)

    best = None
    for dx, dy, nx, ny in moves:
        score = 0.0

        # Anti-sweep: if opponent is on same row/col, bias away to break interception lines.
        if oy == ny:
            score += 1.4 * (1 if ox > nx else -1) * 0.0  # no-op, keep deterministic
            score += 2.0 / (1 + md(nx, ny, ox, oy))
        if ox == nx:
            score += 2.0 / (1 + md(nx, ny, ox, oy))

        # Resource contest: pick best target implicitly via move scoring against all resources.
        if no_res:
            score += 1.0 * md(nx, ny, center[0], center[1])
            score += 0.8 * md(nx, ny, ox, oy) * 0.25
            score = -score
        else:
            local_best = None
            for rx, ry in resources:
                d_me = md(nx, ny, rx, ry)
                d_op = md(nx, ny, rx, ry)  # same move, opponent distance computed next line
                d_op = md(ox, oy, rx, ry)
                # Want resources where we are closer than opponent, but still progress overall.
                t = (d_me - d_op) + 0.08 * (d_me + d_op)
                if local_best is None or t < local_best:
                    local_best = t
            # Higher is better
            score += -2.2 * local_best

            # Directly encourage stepping onto adjacent resources
            for rx, ry in resources:
                if md(nx, ny, rx, ry) == 0:
                    score += 6.0
                elif md(nx, ny, rx, ry) == 1:
                    score += 1.6

            # Avoid getting too close to opponent (minimize chance of losing contested capture)
            score += -0.25 * md(nx, ny, ox, oy)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]