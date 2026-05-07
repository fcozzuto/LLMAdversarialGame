def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def resource_score(rx, ry):
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        # tie-break: prefer smaller self distance, then stable hash
        hsh = ((rx * 17 + ry * 29) ^ (sd * 7)) & 1023
        return (adv, -sd, hsh)

    target = None
    best = None
    # Choose a resource we can realistically contest, otherwise any remaining
    for r in resources:
        key = resource_score(r[0], r[1])
        if best is None or key > best:
            best = key
            target = (r[0], r[1])

    tx, ty = target
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    if observation.get("turn_index", 0) % 2 == 1:
        moves = moves[4:] + moves[:4]  # small deterministic variation

    # Evaluate moves with a "denial" pressure term: don't drift into opponent-favored zones
    center = (w // 2, h // 2)
    opp_d_to_center = md(ox, oy, center[0], center[1])

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        od_to_target = md(ox, oy, tx, ty)
        adv_after = od_to_target - myd  # higher is better

        # If opponent is already close to this target, prioritize moves that reduce their next capture.
        # Approximate by how close opponent would be after the move (they don't move yet, but this biases away).
        opp_shadow = -md(ox, oy, nx, ny)  # farther from opponent is better
        center_bias = -md(nx, ny, center[0], center[1]) if opp_d_to_center > 2 else 0

        # Also: slight penalty for moving away from target direction when diagonal not needed
        direct_pen = -((tx - nx) * (tx - sx) + (ty - ny) * (ty - sy) < 0)

        val = (adv_after, opp_shadow, center_bias, direct_pen, -myd)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]