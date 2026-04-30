def choose_move(observation):
    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    best_r = None
    best_adv = None
    best_ds = None
    for r in resources:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        adv = do - ds
        if best_r is None or adv > best_adv or (adv == best_adv and ds < best_ds):
            best_r, best_adv, best_ds = r, adv, ds

    target = best_r

    best_move = [0, 0]
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            d_to_t = dist((nx, ny), target)
            d_from_opp = dist((nx, ny), (ox, oy))
            # Prefer reducing distance to target; slightly prefer being farther from opponent.
            score = -d_to_t * 10 + d_from_opp * 0.1
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move