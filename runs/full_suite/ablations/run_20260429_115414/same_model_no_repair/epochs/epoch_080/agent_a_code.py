def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a target resource where we are relatively closer than opponent.
    # Key: (my_dist - opp_dist) first, then my_dist, then preference toward center-ish.
    def dist(a, b, x, y):
        return abs(x - a) + abs(y - b)

    best_r = None
    best_key = None
    for rx, ry in resources:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center = abs(rx - cx) + abs(ry - cy)
        key = (md - od, md, center, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    tx, ty = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_d = abs(tx - nx) + abs(ty - ny)
        my_now = abs(tx - sx) + abs(ty - sy)
        # Opponent pressure: compare their distance if they were to move 1 step optimally toward same target.
        opp_now = abs(tx - ox) + abs(ty - oy)
        opp_best = opp_now
        for odx, ody in deltas:
            ex, ey = ox + odx, oy + ody
            if not inb(ex, ey) or (ex, ey) in obs:
                continue
            opp_best = min(opp_best, abs(tx - ex) + abs(ty - ey))

        # Score: prioritize reducing our distance; penalize losing advantage.
        # Also slightly prefer moves that improve our advantage vs opponent.
        my_adv_now = opp_now - my_now
        my_adv_next = opp_best - my_d
        score = (-(my_d), (my_adv_next - my_adv_now), -my_d, dx, dy)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]