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

    best = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        best_adv = None
        best_my = None
        for rx, ry in resources:
            my_d = max(abs(nx - rx), abs(ny - ry))
            op_d = max(abs(ox - rx), abs(oy - ry))
            adv = op_d - my_d  # positive means we are closer than opponent for that resource
            if best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_my):
                best_adv = adv
                best_my = my_d

        od_here = max(abs(nx - ox), abs(ny - oy))
        score = (best_adv * 1.5) - (best_my * 0.35) + (0.03 * od_here) - (0.05 if dx == 0 and dy == 0 else 0)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]