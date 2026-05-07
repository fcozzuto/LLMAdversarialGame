def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if safe(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose move that maximizes guaranteed "advantage" to reach some resource first.
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        my = (nx, ny)
        # Avoid getting too close to opponent unless it helps win a resource.
        opp_dist_now = md(my, (ox, oy))
        min_opp_dist_to_any = min(md((ox, oy), r) for r in resources)
        # Evaluate advantage for the best target under this move.
        best_adv = -10**9
        best_target = None
        for r in resources:
            a = md(my, r)
            b = md((ox, oy), r)
            # If we can reach earlier, advantage positive; else prefer resources where we are closer.
            adv = (b - a)
            if adv > best_adv or (adv == best_adv and a < md((sx, sy), r)):
                best_adv = adv
                best_target = r
        # Combine: favor winning/near-winning targets; slightly penalize approaching opponent.
        val = best_adv * 1000 + (-opp_dist_now) + (-min_opp_dist_to_any)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if best_move != (0, 0) and (dx, dy) == (0, 0):
                continue
            if (dx, dy) == best_move:
                continue
            # Deterministic tie-break: lexicographic (dx,dy)
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]