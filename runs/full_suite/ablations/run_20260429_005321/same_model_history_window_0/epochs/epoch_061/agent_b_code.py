def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    best = (0, 0)
    best_score = -10**18

    opp = (ox, oy)

    # Choose target resource based on who is closer (deterministic contest).
    target = None
    best_gap = -10**18
    for r in resources:
        r = tuple(r)
        sd = dist((sx, sy), r)
        od = dist(opp, r)
        gap = od - sd  # positive means we are closer
        if gap > best_gap or (gap == best_gap and (r[1], r[0]) < (target[1], target[0]) if target else True):
            best_gap = gap
            target = r

    # If no resources, head to center deterministically.
    if not resources:
        target = (w // 2, h // 2)

    cx, cy = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Attraction to target (manhattan), slight tie-break by exact direction.
        d_to_target = dist((nx, ny), (cx, cy))
        # Repulsion from opponent: prefer to increase distance when contest is unclear.
        d_opp = dist((nx, ny), opp)

        # Resource contest heuristic: maximize improvement in being closer to target.
        cur_d = dist((sx, sy), (cx, cy))
        improvement = cur_d - d_to_target  # positive if moving closer

        # Bonus if stepping onto a resource (engine likely handles pickup).
        on_res = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        # If we are not the closest to target originally, prioritize safety + blocking line (approx).
        # Block approximation: prefer moves that increase distance to opponent and reduce opponent's distance to target.
        opp_d_before = dist(opp, (cx, cy))
        opp_d_after = dist(opp, (cx, cy))  # opponent doesn't move this turn, so constant; omit

        safety = d_opp
        score = 1000 * on_res + 20 * improvement - 3 * d_to_target + 2 * safety

        # Deterministic tie-break: prefer staying closer to target in y then x.
        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            if (ny, nx) < (sy + best[1], sx + best[0]):
                best = (dx, dy)

    return [best[0], best[1]]