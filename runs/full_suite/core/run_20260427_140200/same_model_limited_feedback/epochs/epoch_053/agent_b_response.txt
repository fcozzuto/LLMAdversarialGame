def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    ox = set((p[0], p[1]) for p in obstacles)
    x, y = self_pos[0], self_pos[1]
    ax, ay = opp_pos[0], opp_pos[1]

    def dist2(p, q):
        dx = p[0] - q[0]
        dy = p[1] - q[1]
        return dx * dx + dy * dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_s = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in ox:
                    d = dist2((nx, ny), (cx, cy))
                    s = -d
                    if s > best_s:
                        best_s = s
                        best = [dx, dy]
        return best if best is not None else [0, 0]

    best_target = None
    best_adv = -10**18
    for i, r in enumerate(resources):
        rx, ry = r[0], r[1]
        if (rx, ry) in ox:
            continue
        ds = dist2((x, y), (rx, ry))
        do = dist2((ax, ay), (rx, ry))
        # Prefer targets where we are significantly closer than opponent.
        adv = (do - ds) * 1000 - ds - i * 0.001
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in ox:
            continue
        new_ds = dist2((nx, ny), (tx, ty))
        # Also slightly prefer moves that keep us from getting too close to the opponent.
        d_opp = dist2((nx, ny), (ax, ay))
        score = -new_ds + 0.001 * d_opp
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move