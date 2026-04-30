def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist_m(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick resource to maximize chance of arriving first (and not too far).
    best_r = None
    best_val = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist_m(sx, sy, rx, ry)
        do = dist_m(ox, oy, rx, ry)
        val = (do - ds) - 0.12 * ds
        if val > best_val:
            best_val, best_r = val, (rx, ry)
    tx, ty = best_r if best_r is not None else resources[0]

    # Decide whether to block/chase.
    my_to = dist_m(sx, sy, tx, ty)
    op_to = dist_m(ox, oy, tx, ty)
    chase = (op_to < my_to) and (dist_m(sx, sy, ox, oy) <= 3)

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        if chase:
            # Chase opponent while keeping some pressure on target.
            s_opp = -dist_m(nx, ny, ox, oy)
            s_tar = -0.35 * dist_m(nx, ny, tx, ty)
            score = s_opp + s_tar
        else:
            # Move toward target; penalize stepping away and getting into opponent proximity.
            s_tar = -dist_m(nx, ny, tx, ty)
            s_step = -0.15 * dist_m(nx, ny, sx, sy)
            s_opp = -0.12 * dist_m(nx, ny, ox, oy)
            score = s_tar + s_step + s_opp
        if score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]