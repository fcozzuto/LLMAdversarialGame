def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

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

    # Candidate targets: favor resources where we are relatively better, but also
    # prioritize "denial" when opponent is closer.
    cand = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        rel = od - sd
        denial_bias = 18 if od <= sd else -6
        # Small deterministic tie-break by coordinate.
        tieb = (rx * 0.001 + ry * 0.0007)
        val = rel * 30 + denial_bias - sd * 1.2 - od * 0.1 - tieb
        cand.append((val, rx, ry))
    cand.sort(reverse=True)
    top = cand[:min(5, len(cand))]

    best_move = None
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            # Evaluate move by best possible target after moving.
            move_cost = (abs(dx) + abs(dy)) * 0.35
            score = -1e18
            for _, rx, ry in top:
                sd2 = man(nx, ny, rx, ry)
                od2 = man(ox, oy, rx, ry)
                rel2 = od2 - sd2
                denial2 = 20 if od2 <= sd2 else -7
                # Encourage cutting distance and worsening opponent prospects.
                s = rel2 * 28 + denial2 - sd2 * 1.1 + (od2 - sd2) * 0.25 - move_cost
                if s > score:
                    score = s

            # Deterministic tie-break: prefer moves that reduce our distance to the
            # overall best current target, then prefer lexicographically smaller deltas.
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
            elif score == best_score and best_move is not None:
                # Lexicographic tie-break (dx,dy) for determinism.
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move