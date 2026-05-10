def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res_set = {(r[0], r[1]) for r in resources}
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    # Score candidate move by best resource advantage achievable from resulting cell
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        if resources:
            # immediate pick bonus if resource on cell
            pick_bonus = 10**6 if (nx, ny) in res_set else 0
            local_best = -10**18
            for rx, ry in res_set:
                our_d = manh(nx, ny, rx, ry)
                opp_d = manh(ox, oy, rx, ry)
                # maximize opponent being farther and staying close
                val = (opp_d - our_d) * 12 - our_d
                # small tie-break toward closer to center for stability
                cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
                val -= 0.001 * (abs(nx - cx) + abs(ny - cy))
                if our_d == 0:
                    val += 2 * 10**6
                if val > local_best:
                    local_best = val
            score = pick_bonus + local_best
        else:
            # no visible resources: move toward center while staying away from opponent
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            dcen = abs(nx - cx) + abs(ny - cy)
            dopp = manh(nx, ny, ox, oy)
            score = -dcen + 0.01 * dopp

        # Deterministic tie-break: lexicographic on (dx, dy) for equal scores
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]