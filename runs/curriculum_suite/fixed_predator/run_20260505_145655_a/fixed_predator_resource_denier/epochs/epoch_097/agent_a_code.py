def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best_score = None
    best_move = (0, 0)

    for dx, dy, nsx, nsy in cand:
        s_center = abs(nsx - (w - 1) / 2) + abs(nsy - (h - 1) / 2)
        score = -0.01 * s_center
        for rx, ry in resources:
            sd = man(nsx, nsy, rx, ry)
            od = man(ox, oy, rx, ry)

            # Prefer cells where we are closer than opponent; otherwise seek denial by reducing gap.
            base = (od - sd) * 20 - sd
            if od < sd:
                # Opponent is closer to this resource; reward making ourselves less behind.
                base += (sd - od) * 3
            else:
                # We are closer; reward that margin.
                base += (od - sd) * 5

            # Mild tie-break to push toward near resources and reduce wandering.
            base -= 0.05 * sd
            if base > score:
                score = base

        # Secondary: avoid moves that leave us far from all resources.
        min_sd = min(man(nsx, nsy, rx, ry) for rx, ry in resources)
        score -= 0.03 * min_sd

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]