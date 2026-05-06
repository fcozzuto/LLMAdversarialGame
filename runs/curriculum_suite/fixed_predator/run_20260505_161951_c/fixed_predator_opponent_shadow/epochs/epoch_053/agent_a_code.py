def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no resources, deterministically keep distance while drifting to a midline intersection
    if not resources:
        # choose move maximizing safety, tie-break by proximity to midpoint
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in moves:
            safety = md(nx, ny, ox, oy)
            mid = md(nx, ny, tx, ty)
            key = (-safety, mid, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # When resources exist: prioritize increasing advantage on best available resource,
    # and add an explicit repulsion term when opponent is near (shadow predator behavior).
    k_rep = 0.85
    k_adv = 1.25
    k_self = 0.12

    best = (0, 0)
    best_key = None
    for dx, dy, nx, ny in moves:
        opp_d_after = md(nx, ny, ox, oy)
        # repel harder when close
        rep = 0.0
        if opp_d_after <= 3:
            rep = (3 - opp_d_after + 1)  # 1..4
        # compute best advantage over resources from this next cell
        best_adv = -10**9
        best_self_to = 10**9
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)  # opponent "cursor" toward same target
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and self_d < best_self_to):
                best_adv = adv
                best_self_to = self_d
        # score: maximize advantage and safety/repulsion; minimize remaining distance to chosen target
        # Convert to minimization key for determinism.
        score = (-k_adv * best_adv) + (k_self * best_self_to) + ( -k_rep * rep )
        # tie-breakers: prefer moves that increase distance from opponent, then lexical dx,dy
        key = (score, -opp_d_after, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]