def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, head to center while keeping distance from opponent.
    if not resources:
        best = None
        cx = (w - 1) // 2; cy = (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            score = dist((nx, ny), (ox, oy)) + 0.05 * (-(abs(nx - cx) + abs(ny - cy)))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Decide a target: prefer resources where we can reach not later than opponent.
    candidates = []
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        # Bonus for being strictly closer; penalty if opponent already has advantage.
        lead = od - sd
        candidates.append((lead, -sd, r[0], r[1]))
    candidates.sort(reverse=True)
    target = None
    for lead, _, rx, ry in candidates:
        if lead >= 0:
            target = (rx, ry)
            break
    if target is None:
        # All losing: choose the closest resource that minimizes opponent advantage.
        target = (candidates[0][2], candidates[0][3])

    tx, ty = target

    # Evaluate immediate moves: (1) progress to target, (2) avoid walking into opponent,
    # (3) slight bias to deny opponent by increasing their distance while moving.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cur_d = dist((nx, ny), (tx, ty))
        my_gain = -cur_d
        my_dist_opp = dist((nx, ny), (ox, oy))
        opp_push = my_dist_opp  # directly maximize separation
        # If we step onto a cell adjacent to opponent while still not improving, discourage.
        adj_pen = 0
        if my_dist_opp <= 1 and cur_d >= dist((sx, sy), (tx, ty)):
            adj_pen = -2
        # Ensure directional progress preference with tie-break.
        tie = -(abs(nx - tx) + abs(ny - ty))
        score = 3.0 * my_gain + 0.6 * opp_push + adj_pen + 0.05 * tie
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]] if best else [0, 0]