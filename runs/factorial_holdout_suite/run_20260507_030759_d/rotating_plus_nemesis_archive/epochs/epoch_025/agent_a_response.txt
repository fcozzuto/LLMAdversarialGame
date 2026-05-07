def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    res = [(int(r[0]), int(r[1])) for r in resources]
    res.sort()

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        move_score = -10**18
        for tx, ty in res:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Prefer resources we can reach no later than opponent; otherwise deny still-close targets.
            # Large weight on advantage, then smaller distance.
            adv = do - ds
            s = adv * 100 - ds
            if ds <= do:
                s += 250
            else:
                # still allow near competitive targets but less
                s -= (ds - do) * 20
            move_score = s if s > move_score else move_score

        # Small tie-breaker: prefer moves that move generally toward best immediate resource
        # (deterministic and cheap).
        tie_bonus = -min(man(nx, ny, tx, ty) for tx, ty in res)
        move_score += tie_bonus

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]