def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    # Pick a target resource where we are relatively closer than the opponent
    best_r = None
    best_adv = None
    for rx, ry in resources:
        sd = (sx - rx) * (sx - rx) + (sy - ry) * (sy - ry)
        od = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
        # Lower is better: prefer resources we can reach earlier
        adv = sd - 0.95 * od
        if best_adv is None or adv < best_adv:
            best_adv = adv
            best_r = (rx, ry)

    tx, ty = best_r

    # One-step lookahead scoring with obstacle and opponent interference penalties
    best_m = [0, 0]
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        ndt = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        now_d = (sx - tx) * (sx - tx) + (sy - ty) * (sy - ty)
        improvement = now_d - ndt  # prefer reducing distance

        ndo = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        opp_d2 = (ox - tx) * (ox - tx) + (oy - ty) * (oy - ty)

        # If opponent is closer to the same target, prioritize blocking by increasing their distance and
        # keeping our progress toward the target.
        block = 0.0
        if (ox - tx) * (ox - tx) + (oy - ty) * (oy - ty) <= (sx - tx) * (sx - tx) + (sy - ty) * (sy - ty):
            block = 0.002 * ndo

        # Mildly prefer moves that approach target even if opponent pressure exists
        score = 10.0 * improvement + 0.001 * ndo - 0.0005 * ndt + block + (1e-6 * ndt if opp_d2 < now_d else 0.0)

        if best_s is None or score > best_s:
            best_s = score
            best_m = [dx, dy]

    return best_m