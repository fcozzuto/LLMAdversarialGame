def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_key = None

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer center, but also keep distance from opponent.
            key = (cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # Target: resources scored by (opp distance - self distance) then self distance.
    # Aim to step into cells that improve lead while still approaching likely targets.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dself_to_opp = cheb(nx, ny, ox, oy)
        # Best resource from this candidate
        best_r_key = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer than opponent would be to that resource
            # tie-breakers favor reducing distance to the resource and staying relatively safe
            rkey = (-lead, ds, dself_to_opp, rx, ry)
            if best_r_key is None or rkey < best_r_key:
                best_r_key = rkey
        # Candidate preference: maximize lead; also avoid stepping into cells that are much closer to opponent than us
        # (i.e., increase opponent disadvantage)
        # We can infer lead from best_r_key[0] = -lead
        lead_score = best_r_key[0]
        # Deterministic secondary ordering
        cand_key = (lead_score, best_r_key[1], -dself_to_opp, dx, dy)
        if best_key is None or cand_key < best_key:
            best_key = cand_key
            best_move = [dx, dy]

    return best_move