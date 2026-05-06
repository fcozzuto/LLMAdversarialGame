def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = (man(nx, ny, tx, ty), -man(nx, ny, ox, oy))
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Choose a resource where we are likely to beat/contest opponent, then move to improve that contest.
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer: we lead (negative), then closer; also discourage hopeless far-behind targets.
        lead = sd - od
        key = (lead, sd)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best = None
    for dx, dy, nx, ny in moves:
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        opp_dist = man(nx, ny, ox, oy)
        # Main: minimize our distance gap to beat opponent on this resource.
        # Secondary: maximize separation from opponent to avoid being intercepted.
        v = (sd - od, sd, -opp_dist)
        if best is None or v < best[0]:
            best = (v, dx, dy)
    return [best[1], best[2]]