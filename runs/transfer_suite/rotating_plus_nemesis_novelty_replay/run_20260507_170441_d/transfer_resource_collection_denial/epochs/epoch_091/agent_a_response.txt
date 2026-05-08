def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic priority among equal scores: keep as listed order.

    # Choose target: prefer resources we are likely to secure, but also push toward blocking/tempo.
    best = None
    best_val = -10**18
    my_to_center = abs((w - 1) / 2 - sx) + abs((h - 1) / 2 - sy)
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive means we are closer (in Chebyshev)
        # If opponent closer, still consider but strongly reduced.
        v = adv * 900 - my_d * 6 - my_to_center * 0.05
        # Small extra bias for closer resources to reduce dithering.
        if v > best_val:
            best_val = v
            best = (rx, ry)

    tx, ty = best

    # Optionally, if opponent is much closer to our chosen target, pick a different one to contest.
    my_d0 = dist8(sx, sy, tx, ty)
    op_d0 = dist8(ox, oy, tx, ty)
    if op_d0 < my_d0 - 1:
        best2 = best
        best_val2 = best_val
        for rx, ry in resources:
            my_d = dist8(sx, sy, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            adv = op_d - my_d
            v = adv * 900 - my_d * 6 - (adv < 0) * 200 - my_to_center * 0.05
            if v > best_val2:
                best_val2 = v
                best2 = (rx, ry)
        tx, ty = best2

    # Select move that minimizes distance to target and improves security margin versus opponent.
    # Use move evaluation with a slight repulsion from obstacles' neighborhood (cheap).
    def obst_rep(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obst:
                    r += 1
        return r

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = dist8(nx, ny, tx, ty)
        op_d = dist8(ox, oy, tx, ty)
        # Prefer moves that keep/extend being closer to the target.
        score = my_d * 10 - (op_d - my_d) * 6 + obst_rep(nx, ny) * 2
        # If stepping onto a resource would happen, it should be best.
        if (nx, ny) in resources:
            score -= 50
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]