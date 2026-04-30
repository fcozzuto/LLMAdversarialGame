def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ex, ey = int(p[0]), int(p[1])
            if 0 <= ex < w and 0 <= ey < h:
                obstacles.add((ex, ey))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        resources = [(sx, sy)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda t: (t[0] * 7 + t[1] * 11) % 13)

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_to_res = []
    for rx, ry in resources:
        do = dist(ox, oy, rx, ry)
        opp_to_res.append((do, rx, ry))
    opp_to_res.sort()

    # Consider up to a few closest resources to avoid brittle global search
    top = opp_to_res[:6]
    top_resources = [(rx, ry, do) for (do, rx, ry) in top]

    best = None
    best_val = -10**18
    ti = int(observation.get("turn_index", 0) or 0)

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Value: win-preference on resources where we are not farther than opponent;
        # also keep some distance from opponent when it threatens contested pickups.
        val = 0.0
        my_op_dist = dist(nx, ny, ox, oy)
        val -= 0.08 * my_op_dist

        contest_bonus = 0.0
        for rx, ry, do in top_resources:
            dm = dist(nx, ny, rx, ry)
            # If we are closer or tied, encourage; if we are farther, penalize a lot (target elsewhere).
            if dm <= do:
                contest_bonus += (do - dm) + 1.0
                val += 3.0 / (dm + 1.0)
            else:
                val -= 2.2 / (dm + 1.0)
        # Additional shaping: slightly prefer positions that are closer to the closest "winnable" resource
        if contest_bonus > 0:
            best_d = min(dist(nx, ny, rx, ry) for rx, ry, do in top_resources if dist(nx, ny, rx, ry) <= do)
            val += 1.2 / (best_d + 1.0)
        else:
            # If no winnable resource among top, drift toward the closest overall while not dying to opponent
            best_d = min(dist(nx, ny, rx, ry) for rx, ry, do in top_resources)
            val += 0.6 / (best_d + 1.0)

        # Deterministic tie-break
        val += ((ti + i) % 7) * 1e-6

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]