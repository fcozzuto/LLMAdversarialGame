def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set((a, b) for a, b in observation["obstacles"])
    resources = observation["resources"]

    def sgn(v):
        return (v > 0) - (v < 0)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_target = None
    best_adv = None
    best_opp = None
    if resources:
        for rx, ry in resources:
            self_d = max(abs(rx - x), abs(ry - y))
            opp_d = max(abs(rx - ox), abs(ry - oy))
            adv = opp_d - self_d
            if best_target is None or adv > best_adv or (adv == best_adv and self_d < best_opp):
                best_target = (rx, ry)
                best_adv = adv
                best_opp = self_d
    else:
        best_target = (ox, oy)  # fallback

    tx, ty = best_target
    step = (sgn(tx - x), sgn(ty - y))

    def legal(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles

    # Prefer greedy step toward target, then best alternative that reduces distance to target.
    cand_moves = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if legal(nx, ny):
            dist = max(abs(tx - nx), abs(ty - ny))
            cand_moves.append((dist, dx, dy))
    if not cand_moves:
        return [0, 0]

    # If greedy is legal, bias toward it.
    gx, gy = step
    greedy = (gx, gy)
    for dist, dx, dy in cand_moves:
        if (dx, dy) == greedy:
            # small tie-break: also prefer moving away from opponent if equal distance
            opp_dist = max(abs(ox - (x + dx)), abs(oy - (y + dy)))
            return [dx, dy] if best_adv is not None else [dx, dy]

    # Deterministic tie-breakers: lower target distance, then higher advantage (opp_dist - self_dist after move), then dx,dy.
    best = None
    for dist, dx, dy in cand_moves:
        nx, ny = x + dx, y + dy
        self_d = max(abs(tx - nx), abs(ty - ny))
        opp_d = max(abs(tx - ox), abs(ty - oy))  # fixed for tie flavor
        adv = opp_d - self_d
        key = (self_d, -adv, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]