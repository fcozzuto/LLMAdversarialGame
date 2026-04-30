def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        da = ax - bx
        db = ay - by
        return da * da + db * db

    # Pick best resource target by maximizing "we get there first" potential for our next step.
    def cell_valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    best_move = [0, 0]
    best_score = -10**18
    opp_x, opp_y = ox, oy

    # Precompute a deterministic "secondary" target: nearest resource by our distance.
    nearest_r = None
    nearest_rd = 10**18
    for r in resources:
        rx, ry = r[0], r[1]
        d = cheb(sx, sy, rx, ry)
        if d < nearest_rd:
            nearest_rd = d
            nearest_r = (rx, ry)

    if not resources:
        # Move toward opponent while avoiding obstacles
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not cell_valid(nx, ny):
                continue
            score = -cheb(nx, ny, opp_x, opp_y)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # Evaluate each possible move against the best resource for that move.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_valid(nx, ny):
            continue

        # Primary: find resource where (opponent - us) distance is maximized after our move.
        best_adv = -10**18
        best_r_dist_term = 10**18
        for r in resources:
            rx, ry = r[0], r[1]
            dm = cheb(nx, ny, rx, ry)   # squared dist for ours
            do = cheb(opp_x, opp_y, rx, ry)  # squared dist for opponent
            adv = do - dm  # positive => we are closer than opponent
            # Prefer higher advantage; if tie, prefer closer to resource.
            if adv > best_adv or (adv == best_adv and dm < best_r_dist_term):
                best_adv = adv
                best_r_dist_term = dm

        # Secondary: also gently prefer moving toward a nearest resource if no strong advantage exists.
        target_bonus = 0
        if nearest_r is not None:
            tx, ty = nearest_r
            target_bonus = -cheb(nx, ny, tx, ty)

        # Also avoid "stalling" when there is a clearly better move.
        move_cost = 0 if (dx == 0 and dy == 0) else 1

        score = best_adv * 1000 + target_bonus + move_cost
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move