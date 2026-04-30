def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = -10**18

    # Pick a target resource that we can reach relatively sooner than the opponent.
    # Use squared distances for determinism and speed.
    if resources:
        t_score = []
        for rx, ry in resources:
            ds = dist2(sx, sy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Smaller ds - do => we are advantaged.
            t_score.append((ds - do, ds + do * 0.05, rx, ry))
        t_score.sort()
        tx, ty = t_score[0][2], t_score[0][3]
    else:
        # If no resources visible, head toward center to reduce opponent blocking dominance.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Main objective: minimize our distance to target, while maximizing relative advantage.
        ds_new = dist2(nx, ny, tx, ty)
        ds_now = dist2(sx, sy, tx, ty)
        do = dist2(ox, oy, tx, ty)
        adv_now = dist2(sx, sy, tx, ty) - dist2(ox, oy, tx, ty)
        adv_new = ds_new - do

        # Secondary: avoid letting opponent easily grab nearby resources by not stepping
        # too close to them unless it improves relative advantage.
        dso = dist2(nx, ny, ox, oy)
        opp_pen = 0
        if dso <= 4:  # within 2 tiles (squared)
            opp_pen = 50

        # Small preference to keep moving (if equal, prefer closer to target).
        move_bonus = 0
        if dx != 0 or dy != 0:
            move_bonus = 1

        sc = 0
        sc += (adv_now - adv_new) * 10  # improve relative advantage
        sc += (ds_now - ds_new) * 2     # improve distance to target
        sc += -opp_pen
        sc += -0.1 * ds_new
        sc += move_bonus

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]