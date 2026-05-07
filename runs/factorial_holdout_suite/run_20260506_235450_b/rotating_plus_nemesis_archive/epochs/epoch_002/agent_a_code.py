def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [])

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        da = cheb(sx, sy, rx, ry)
        db = cheb(ox, oy, rx, ry)
        # Higher is better: we prefer resources where we are relatively closer,
        # but also prefer those we can reach quickly at all.
        score = (db - da) * 1000 + (1.0 / (da + 1)) * 200 + (1.0 / (db + 1)) * -50 - (rx + ry) * 1e-6
        if best is None or score > best[0]:
            best = (score, rx, ry)

    tx, ty = best[1], best[2]
    opp_to_target = cheb(ox, oy, tx, ty)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cur_best = None
    cur_move = (0, 0)

    # Move choice maximizes post-move "capture pressure" and avoids walking into obstacles.
    # Includes a strong bonus if we can land on the resource this turn.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d = cheb(nx, ny, tx, ty)
        # We want to reduce our distance and also keep the opponent farther relative to us.
        sc = (opp_to_target - our_d) * 120
        sc += (1.0 / (our_d + 1)) * 80
        # If opponent could potentially get closer as we move, penalize less (deterministic proxy):
        opp_d_next_proxy = cheb(ox, oy, tx, ty)  # opponent move unknown; use current as stable proxy
        sc += (1.0 / (opp_d_next_proxy + 1)) * -10
        if (nx, ny) == (tx, ty):
            sc += 100000
        # Tiny tie-breaker to stabilize behavior deterministically
        sc -= (abs(dx) + abs(dy)) * 0.01
        if cur_best is None or sc > cur_best:
            cur_best = sc
            cur_move = (dx, dy)

    return [int(cur_move[0]), int(cur_move[1])]