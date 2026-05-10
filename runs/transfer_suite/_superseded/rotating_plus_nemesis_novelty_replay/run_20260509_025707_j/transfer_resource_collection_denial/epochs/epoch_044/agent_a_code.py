def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Pick a target: either a resource we can likely secure, else the resource opponent is closest to (denial).
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0.0
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # If we are ahead, prioritize and prefer nearer.
            if sd < od:
                lead = od - sd
                score += 8.0 * lead - 0.25 * sd
            else:
                # If opponent is ahead, deny by moving toward their nearest resource and increasing their effort.
                gap = sd - od
                # Deny reward: being closer than before to their target, and discouraging easy capture.
                score += 1.6 / (1.0 + gap) - 0.18 * od + 0.05 * sd

        # Minor tie-break: prefer moves that get closer to the globally closest secure candidate.
        # (Deterministic, keeps some directionality.)
        closest_opp_res = min(resources, key=lambda rr: man(ox, oy, rr[0], rr[1]))
        score -= 0.02 * man(nx, ny, closest_opp_res[0], closest_opp_res[1])

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]