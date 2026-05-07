def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    res = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Precompute resource tuples
    resources = []
    for r in res:
        try:
            resources.append((r[0], r[1]))
        except:
            pass

    if not resources:
        # No resources: just move toward center-ish while staying valid
        tx, ty = w // 2, h // 2
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if -d > best[0]:
                best = (-d, dx, dy)
        return [best[1], best[2]]

    def opp_exists():
        return ox is not None and oy is not None

    opp_ok = opp_exists()

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate best resource for us after this move, with competitive advantage check
        val = 0
        closest = 10**9
        for rx, ry in resources:
            d_us = abs(nx - rx) + abs(ny - ry)
            if d_us < closest:
                closest = d_us
            if opp_ok:
                d_opp = abs(ox - rx) + abs(oy - ry)
                # Prefer resources where we are not behind; strong penalty if opponent closer
                if d_us <= d_opp:
                    val += 18 - d_us
                else:
                    val -= 26 + (d_us - d_opp)
            else:
                val += 10 - d_us

        # Small tie-break: don't drift away from current nearest resource
        val += -closest
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]