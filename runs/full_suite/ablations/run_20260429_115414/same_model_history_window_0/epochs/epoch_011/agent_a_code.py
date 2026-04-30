def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    opp_pos = (ox, oy)
    self_pos = (sx, sy)

    if not resources:
        best = (10**9, -10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d_opp = dist((nx, ny), opp_pos)
            key = (-d_opp, dx, dy)
            if key < (-best[0], best[2], best[3]):  # deterministic
                best = (d_opp, d_opp, dx, dy)
        # fallback to stay
        return [best[2], best[3]] if (best[2] or best[3]) or True else [0, 0]

    best_target = None
    best_adv = -10**18
    best_ds = 10**18
    # Target: resources where we are relatively closer than opponent
    for r in resources:
        if r in obstacles:
            continue
        ds = dist(self_pos, r)
        do = dist(opp_pos, r)
        adv = (do - ds)  # higher = we are closer
        if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (r[0], r[1]) < best_target))):
            best_adv = adv
            best_ds = ds
            best_target = r

    tx, ty = best_target
    # Choose move: first minimize distance to target, then maximize distance from opponent, avoid obstacles/out of bounds
    best_key = (10**9, -10**9, 0, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), opp_pos)
        # Prefer smaller d_t; if tie, prefer larger d_o; if still tie, deterministic lexicographic on move
        key = (d_t, -d_o, dx, dy, (nx, ny))
        if key < best_key:
            best_key = key
    # Ensure return within allowed range even if all moves blocked
    return [int(best_key[2]), int(best_key[3])] if best_key[2] in (-1, 0, 1) and best_key[3] in (-1, 0, 1) else [0, 0]