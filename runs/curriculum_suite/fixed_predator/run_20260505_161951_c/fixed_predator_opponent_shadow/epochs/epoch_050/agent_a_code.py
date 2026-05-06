def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no visible resources, contest the midline (avoiding obstacles implicitly via move legality)
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in moves:
            dmid = man(nx, ny, tx, ty)
            dovr = man(nx, ny, ox, oy)
            key = (dmid, dovr, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Opportunistic intercept: choose move that improves our lead on the best resource,
    # but prioritizes resources where we are (or can become) earlier than opponent.
    best_move = (0, 0)
    best_val = -10**18
    best_tie = None
    for dx, dy, nx, ny in moves:
        v = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Leading is good; also reduce absolute distance and avoid "giving" by emphasizing opponent delay.
            lead = do - ds
            cand = lead * 10 - ds
            # If we are tied, prefer the one that keeps us slightly closer next turn (tie-break by ds)
            if lead == 0:
                cand -= 2
            if cand > v:
                v = cand
        # Secondary: prefer moves that get us closer to the current best-improving cell (deterministic)
        # Tie-break by opponent distance to center of resources to reduce opponent counterplay deterministically.
        # Compute quick proxy center
        cx = sum(r[0] for r in resources) // len(resources)
        cy = sum(r[1] for r in resources) // len(resources)
        dopp_center = man(nx, ny, cx, cy)
        key = (-(v), dopp_center, man(nx, ny, ox, oy), dx, dy)
        if best_tie is None or key < best_tie:
            best_tie = key
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]