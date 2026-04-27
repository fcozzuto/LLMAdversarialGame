def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    res_set = set((x, y) for x, y in resources)
    obs_set = set((x, y) for x, y in obstacles)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for diagonal

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    # Choose target: prefer resources where we are closer than opponent
    if resources:
        best = None
        for rx, ry in resources:
            our_d = dist((sx, sy), (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))
            advantage = opp_d - our_d
            key = (-advantage, our_d, rx, ry)  # deterministic
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources: drift toward center while keeping distance from opponent
        tx, ty = (w // 2, h // 2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs_set:
            continue
        our_d = dist((nx, ny), (tx, ty))
        opp_d_after = dist((nx, ny), (ox, oy))
        # Primary: minimize distance to target; Secondary: avoid opponent; Tertiary: deterministic tie-break
        score = (our_d, -opp_d_after, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move