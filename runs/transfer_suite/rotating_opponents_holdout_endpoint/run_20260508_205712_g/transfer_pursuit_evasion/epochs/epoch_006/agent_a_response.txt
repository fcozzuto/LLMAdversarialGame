def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs_set.add((int(a[0]), int(a[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    obs_list = list(obs_set)

    def min_obstacle_manhattan(x, y):
        if not obs_list:
            return 999
        m = 999
        for ox2, oy2 in obs_list:
            d = abs(x - ox2) + abs(y - oy2)
            if d < m:
                m = d
        return m

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("run" in role) or ("esc" in role)
    is_pursuer = ("purs" in role) or ("catch" in role) or ("pred" in role)
    if not is_evader and not is_pursuer:
        is_evader = True  # adapt to wall-runner by defaulting to evasive policy

    # Wall-runner evasion/pursuit: cut off corners by preferring moves that change axis toward/away from opponent.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = mobility(nx, ny)
        mob_factor = mob - 2  # dead-ish positions penalized slightly
        md_obs = min_obstacle_manhattan(nx, ny)
        # Prefer being farther from obstacles if evader; closer if pursuer (to use walls).
        obstacle_term = md_obs if not is_evader else -md_obs

        # Axis-bias: prioritize reducing/increasing Chebyshev distance component-wise.
        cheb = max(abs(nx - ox), abs(ny - oy))
        center_bias = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)

        if is_evader:
            score = (dist2 * 1.2) + (cheb * 0.5) + (mob_factor * 0.8) + (obstacle_term * 0.05) - (center_bias * 0.02)
        else:
            score = (-dist2 * 1.1) + (-cheb * 0.4) + (mob_factor * 0.5) + (obstacle_term * 0.03) + (center_bias * -0.01)

        # Deterministic tie-break: fixed ordering by deltas list, then lexicographic move.
        candidates.append((score, dx, dy, nx, ny))

    candidates.sort(key=lambda t: (-t[0], deltas.index((t[1], t[2])), t[1], t[2]))
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]