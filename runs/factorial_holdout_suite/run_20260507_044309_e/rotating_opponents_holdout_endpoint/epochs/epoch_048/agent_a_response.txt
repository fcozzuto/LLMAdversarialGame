def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive if we are closer
        # prefer resources we can reach first; break ties by nearer and then by coords
        key = (lead > 0, lead, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_step = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        sd2 = man(nx, ny, tx, ty)
        sd_now = man(sx, sy, tx, ty)
        od2 = man(ox, oy, tx, ty)

        # main goal: reduce our distance; secondary: don't let opponent become closer
        # also avoid steps that "waste" progress.
        progress = sd_now - sd2
        deny = (od2 - sd2)
        score = (progress, deny, -sd2, -abs(ox - nx) - abs(oy - ny), -nx, -ny)

        if best_score is None or score > best_score:
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]