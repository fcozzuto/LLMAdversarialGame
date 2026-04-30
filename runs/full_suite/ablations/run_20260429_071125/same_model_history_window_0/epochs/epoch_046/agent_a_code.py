def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target resource where we are relatively closer than the opponent.
    best_r = None
    best_val = -10**9
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        val = (d_op - d_me) * 10 - d_me
        if val > best_val:
            best_val = val
            best_r = (rx, ry)
    if best_r is None:
        # No resources visible: move away from opponent while respecting obstacles.
        target_dx, target_dy = -1 if ox > sx else (1 if ox < sx else 0), -1 if oy > sy else (1 if oy < sy else 0)
        return [target_dx, target_dy]

    tx, ty = best_r

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_me = man(nx, ny, tx, ty)
        d_op = man(ox, oy, tx, ty)

        # Prefer stepping toward target; if opponent is also close, bias away to deny contention.
        content_score = (d_op - d_me) * 6

        # Minor obstacle avoidance via local penalty: if next-next likely blocked, reduce slightly.
        local_pen = 0
        for mx, my in moves:
            ex, ey = nx + mx, ny + my
            if inb(ex, ey) and (ex, ey) in obstacles:
                local_pen += 0.15

        # Prefer not to move adjacent too tightly to opponent unless it helps reach target.
        adj = max(abs(nx - ox), abs(ny - oy)) <= 1
        opp_pen = 3.5 if adj and content_score < 10 else 0

        # If moving onto a resource, huge reward.
        res_on = 20 if (nx, ny) in set(tuple(p) for p in resources) else 0

        score = (-d_me) + content_score + res_on - local_pen - opp_pen

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]