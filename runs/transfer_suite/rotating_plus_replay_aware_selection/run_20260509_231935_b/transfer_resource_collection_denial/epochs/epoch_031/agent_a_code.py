def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res_set = set(tuple(p) for p in resources)

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Take immediate resource if reachable in one move.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            return [dx, dy]

    if not resources:
        return [0, 0]

    # Choose target that we can reach earlier than opponent; tie-break deterministically.
    best = None
    for rx, ry in resources:
        sd = dist_cheb(sx, sy, rx, ry)
        od = dist_cheb(ox, oy, rx, ry)
        advantage = sd - od  # smaller is better (we want sd <= od)
        # Slight bias toward closer absolute targets to prevent dithering.
        val = (round(advantage * 1000), sd, rx, ry)
        if best is None or val < best[0]:
            best = (val, rx, ry)
    _, tx, ty = best

    # Greedy step: move to reduce our distance to target, with obstacle avoidance.
    best_m = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = dist_cheb(nx, ny, tx, ty)
        d_opp = dist_cheb(nx, ny, ox, oy)
        # Prefer moves that keep/strengthen our lead on the target.
        lead_next = d_self - dist_cheb(ox, oy, tx, ty)
        cand = (lead_next, d_self, -d_opp, dx, dy)
        if cand < best_m:
            best_m = cand

    return [best_m[3], best_m[4]]