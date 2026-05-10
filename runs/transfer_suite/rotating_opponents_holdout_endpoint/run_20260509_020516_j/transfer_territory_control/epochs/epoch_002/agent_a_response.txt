def choose_move(observation):
    W = observation.get("grid_width", 0) or 0
    H = observation.get("grid_height", 0) or 0
    if W <= 0 or H <= 0:
        return [0, 0]
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [x, y])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for c in obstacles:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obs.add((c[0], c[1]))

    self_t = observation.get("self_territory", []) or []
    opp_t = observation.get("opponent_territory", []) or []
    self_set = set((c[0], c[1]) for c in self_t if isinstance(c, (list, tuple)) and len(c) >= 2)
    opp_set = set((c[0], c[1]) for c in opp_t if isinstance(c, (list, tuple)) and len(c) >= 2)

    center_x = (W - 1) / 2.0
    center_y = (H - 1) / 2.0

    def score(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        d_center = (nx - center_x) * (nx - center_x) + (ny - center_y) * (ny - center_y)
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        if (nx, ny) in opp_set:
            flip_bonus = 1200
            edge_bonus = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    ax, ay = nx + dx, ny + dy
                    if 0 <= ax < W and 0 <= ay < H and (ax, ay) not in opp_set and (ax, ay) not in self_set:
                        edge_bonus += 35
            return flip_bonus + edge_bonus + (-0.8 * d_center) + (-0.2 * d_opp)

        if (nx, ny) in self_set:
            return 30 + (-0.6 * d_center) + (-0.05 * d_opp)

        return 120 + (-1.0 * d_center) + (5.0 / (1 + d_opp))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs:
                moves.append((score(nx, ny), dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    best_dx, best_dy = moves[0][1], moves[0][2]

    if observation.get("turn_index", 0) % 10 == 9:
        nx, ny = x + best_dx, y + best_dy
        if (nx, ny) in opp_set:
            return [best_dx, best_dy]

    return [best_dx, best_dy]