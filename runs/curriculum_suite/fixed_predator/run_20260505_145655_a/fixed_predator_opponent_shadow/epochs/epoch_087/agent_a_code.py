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

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift to reduce distance to opponent (deterministic).
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Pick a target resource we can reach with advantage; if none, pick the least-bad.
    best_r = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = manhattan((x, y), (tx, ty))
        d_opp = manhattan((ox, oy), (tx, ty))
        advantage = d_opp - d_me
        # Prefer large advantage; then closer to us; then lexicographic.
        key = (advantage, -d_me, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_r = r
    tx, ty = best_r[0], best_r[1]

    # Evaluate all possible next moves with obstacle and horizon penalties.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            val = (-10**9, 0)  # force avoid; engine would also keep us, but don't want it
        else:
            d_me1 = abs(tx - nx) + abs(ty - ny)
            d_opp1 = abs(tx - ox) + abs(ty - oy)
            # Main: maximize (opp_dist - our_dist); secondary: minimize our dist; tertiary: avoid being too close to opponent.
            adv = d_opp1 - d_me1
            val = (adv, -d_me1)
            # Add mild penalty if this step moves away from the target (to stabilize).
            if d_me1 > abs(tx - x) + abs(ty - y):
                val = (val[0] - 1, val[1])
            # Slightly penalize proximity to obstacles to reduce collision streaks.
            near_obs = 0
            for ox0, oy0 in obs_list:
                if abs(ox0 - nx) <= 1 and abs(oy0 - ny) <= 1:
                    near_obs += 1
            if near_obs:
                val = (val[0] - near_obs, val[1])
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]