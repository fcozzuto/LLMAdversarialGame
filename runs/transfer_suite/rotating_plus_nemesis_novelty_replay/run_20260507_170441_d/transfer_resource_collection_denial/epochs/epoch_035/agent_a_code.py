def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_best = None
        my_best_opp = None
        for rx, ry in resources:
            md = max(abs(nx - rx), abs(ny - ry))
            od = max(abs(ox - rx), abs(oy - ry))
            if my_best is None or md < my_best or (md == my_best and od > my_best_opp):
                my_best = md
                my_best_opp = od

        # Prefer moves that win resource races (opponent farther), then minimize own distance.
        race_margin = (my_best_opp - my_best) if (my_best is not None and my_best_opp is not None) else 0
        dist_pen = my_best if my_best is not None else 0

        # Small tie-breakers: move toward nearest resource and reduce staying still.
        od_self = max(abs(nx - ox), abs(ny - oy))
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        score = 5.0 * race_margin - 0.6 * dist_pen + 0.08 * od_self - 0.1 * stay_pen

        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]