def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Interception/steal: focus on resources closest to opponent and move to minimize our distance to them,
    # preferring moves that reduce (our_dist - opp_dist).
    opp_sorted = sorted(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    targets = opp_sorted[:3] if len(opp_sorted) >= 3 else opp_sorted

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate against worst-case (hardest) target among the top ones: robust stealing attempt.
        worst = None
        for tx, ty in targets:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            diff = sd - od  # smaller means closer than (or similar to) opponent
            key = (diff, sd, -od)
            if worst is None or key > worst:
                worst = key

        # Prefer the move with smallest "worst target" key.
        if best is None or worst < best:
            best = worst
            best_move = [dx, dy]

    return best_move