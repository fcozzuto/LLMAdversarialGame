def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = observation.get("resources", [])

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick a small set of candidate targets near us to keep deterministic and cheap
    if resources:
        rs = sorted(resources, key=lambda p: dist2(x, y, p[0], p[1]))
        targets = rs[:min(5, len(rs))]
    else:
        targets = []

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not clamp_in(nx, ny):
            continue

        if targets:
            move_score = -10**18
            for tx, ty in targets:
                self_d = dist2(nx, ny, tx, ty)
                opp_d = dist2(ox, oy, tx, ty)
                # Prefer moves that get us toward resources we are relatively closer to than opponent
                # and also slightly prefer shorter remaining path to that resource.
                rel = opp_d - self_d
                sc = rel * 10 - self_d + (10 if (tx, ty) in targets else 0)
                if sc > move_score:
                    move_score = sc
            # Extra mild anti-collision / anti-lockstep: don't allow getting too close to opponent
            opp_after = dist2(nx, ny, ox, oy)
            move_score += -2 * max(0, 25 - opp_after)
        else:
            # No resources: drift to increase distance from opponent, otherwise to center.
            opp_after = dist2(nx, ny, ox, oy)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            move_score = opp_after - 0.01 * center

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]