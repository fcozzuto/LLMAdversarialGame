def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev (diagonals allowed)

    # Pick a resource where we have the biggest pursuit advantage over opponent
    best = None
    best_adv = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        adv = do - ds  # positive means we are closer
        # tie-break toward nearer and then lexicographic
        key = (adv, -ds, -rx, -ry)
        if best is None or key > best_adv:
            best_adv = key
            best = (rx, ry)

    tx, ty = best

    # Choose move that gets us closest to target, avoids obstacles; also mild anti-chase if opponent is closer
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    opp_ds_now = dist((ox, oy), (tx, ty))
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = dist((nx, ny), (tx, ty))
        # prefer keeping/creating advantage over opponent
        after_adv = opp_ds_now - ns
        score = (after_adv, -ns, -abs(nx - (w//2)), -abs(ny - (h//2)), dx, dy)
        scored.append((score, [dx, dy]))
    if not scored:
        return [0, 0]
    scored.sort(reverse=True)
    return scored[0][1]