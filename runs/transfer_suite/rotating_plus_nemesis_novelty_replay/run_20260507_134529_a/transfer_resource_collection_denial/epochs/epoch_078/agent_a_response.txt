def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    blocked = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose the resource to contest: prefer nearest that opponent is not already much closer to.
    if resources:
        scored = []
        for r in resources:
            sd = md((sx, sy), r)
            od = md((ox, oy), r)
            # Contest priority: closer for us; strongly prefer resources we're not behind on.
            scored.append((sd - 0.9 * max(0, od - sd), sd, od, r))
        scored.sort(key=lambda t: (t[0], t[1], -t[2], t[3][0], t[3][1]))
        target = scored[0][3]
    else:
        target = (ox, oy)

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Primary: reduce distance to target (resource or opponent fallback)
        val = md((nx, ny), target)

        # Secondary: if resources exist, actively deny the currently best contested resource(s)
        if resources:
            # Deny by increasing the chance we are not behind for the closest few resources.
            for r in resources:
                if val < 2:
                    break
                sd = md((nx, ny), r)
                od = md((ox, oy), r)
                behind = sd - od
                if behind > 0:
                    val += 2.5 * behind  # penalize being further than opponent
                else:
                    val += 0.2 * behind  # slight reward for being ahead

            # Prefer staying farther from opponent when contesting (prevents interception)
            val += 0.04 * (10 - md((nx, ny), (ox, oy)))

        # Tertiary tie-break: deterministic towards upper-left (stable ordering)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move