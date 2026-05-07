def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        move_score = -10**18
        for r in resources:
            tx, ty = int(r[0]), int(r[1])
            ds = dist(nx, ny, tx, ty)
            do = dist(ox, oy, tx, ty)
            adv = do - ds  # positive means we are closer than opponent from next step
            # Encourage winning a resource (adv positive), discourage long travel; deterministic tie-break by resource position.
            sc = adv * 1200 - ds * 6 + (-(tx + 2 * ty))
            if sc > move_score:
                move_score = sc

        # If move doesn't secure any advantageous target, still pick one with best (least) our distance and some advantage.
        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    # If all moves invalid (rare), stay.
    return best_move