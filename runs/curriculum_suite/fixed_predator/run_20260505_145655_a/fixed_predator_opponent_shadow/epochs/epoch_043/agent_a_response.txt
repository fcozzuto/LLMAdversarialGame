def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def best_target_value(px, py):
        if not resources:
            return -10**18
        best = None
        for tx, ty in resources:
            d_me = abs(tx - px) + abs(ty - py)
            d_opp = abs(tx - ox) + abs(ty - oy)
            lead = d_opp - d_me
            # Prefer clear advantage and also slightly prefer closer resources for speed
            val = lead * 1000 - d_me + 0.05 * d_opp
            if best is None or val > best[0] or (val == best[0] and (d_opp, d_me, tx, ty) < (best[1], best[2], best[3], best[4])):
                best = (val, d_opp, d_me, tx, ty)
        return best[0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if blocked(nx, ny):
            continue
        # New one-step evaluation: maximize advantage from the moved position, but avoid walking into the opponent
        v = best_target_value(nx, ny)
        d_opp_now = abs(nx - ox) + abs(ny - oy)
        d_opp_cur = abs(x - ox) + abs(y - oy)
        # If opponent is closer after the move, apply a penalty to keep us from feeding into their runs
        penalty = 0
        if d_opp_now < d_opp_cur:
            penalty = (d_opp_cur - d_opp_now) * 25
        # Also add a tiny tie-break preferring staying closer to mid-board for stability
        mid_bias = -(abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2))) * 0.001
        score = v - penalty + mid_bias
        cand.append((score, dx, dy))

    if not cand:
        # All blocked: deterministic retreat/hold
        return [0, 0]

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]