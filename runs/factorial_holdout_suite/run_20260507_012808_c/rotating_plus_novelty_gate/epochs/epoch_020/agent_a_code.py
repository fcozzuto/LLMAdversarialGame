def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    res = [tuple(p) for p in resources]
    if not res:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    best_tiebreak = 10**9

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        self_on_res = 1 if (nx, ny) in res else 0
        best_target_val = -10**18
        best_my_d = 10**9

        for r in res:
            myd = d((nx, ny), r)
            opd = d((ox, oy), r)

            # Prefer immediate pickup, then strong lead; avoid targets where opponent is much closer.
            lead = opd - myd
            target_val = self_on_res * 10000
            target_val += (lead * 60) + (120 - myd) - (15 * max(0, (myd - opd)))
            # If opponent is already very close, discourage (denier behavior).
            if opd <= 2 and myd > opd:
                target_val -= 300
            # Prefer closer winning targets when margins tie.
            if target_val > best_target_val or (target_val == best_target_val and myd < best_my_d):
                best_target_val = target_val
                best_my_d = myd

        # Slightly discourage walking into corners away from race opportunities.
        # This is deterministic and small, but helps avoid "do-nothing" repetition.
        center_dist = abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)
        val = best_target_val - int(center_dist * 2)

        if val > best_val or (val == best_val and best_my_d < best_tiebreak):
            best_val = val
            best_tiebreak = best_my_d
            best_move = (mx, my)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]