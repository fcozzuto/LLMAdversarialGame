def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def parse_pos(p):
        try:
            if isinstance(p, dict):
                x = p.get("x", p.get("X", p.get("col", p.get("cx", 0))))
                y = p.get("y", p.get("Y", p.get("row", p.get("cy", 0))))
            else:
                x, y = p[0], p[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        except Exception:
            pass
        return None

    resources = []
    for r in (observation.get("resources", []) or []):
        rp = parse_pos(r)
        if rp is not None:
            resources.append(rp)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        op = parse_pos(o)
        if op is not None:
            obstacles.add(op)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    parity = (sx + sy) & 1

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = -10**18

    opp_par = (ox + oy) & 1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Base: stay safe from nearby obstacles
        near_pen = 0
        for ox2, oy2 in obstacles:
            if abs(ox2 - nx) <= 1 and abs(oy2 - ny) <= 1:
                near_pen += 6

        # Choose a resource to "commit" to this turn (evaluated by advantage after the move)
        commit = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            if (rx + ry) & 1 == parity:
                adv += 2
            if (rx + ry) & 1 == opp_par:
                adv -= 0.5
            # Prefer nearer targets to avoid diagonal probing snatching far ones
            val = adv * 2 - 0.15 * sd
            if val > commit:
                commit = val

        # If committed target is weak, bias towards improving distance to the best available resource
        if commit < -1000:
            # Shouldn't happen, but keep deterministic
            commit = -man(nx, ny, sx, sy)

        total = commit - near_pen
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]