def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("escape" in self_role)
    is_pursuer = ("pursuer" in self_role) or ("pursue" in self_role) or ("pursuit" in self_role)
    if not is_evader and not is_pursuer:
        is_evader = ("evader" in opp_role) or ("evasion" in opp_role) or ("escape" in opp_role)
        is_pursuer = not is_evader

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Greedy target: pursuer minimizes distance; evader maximizes distance.
    # Small deterministic "wall runner": prefer continuing direction when possible.
    best = None
    best_score = None

    base_dist = abs(sx - ox) + abs(sy - oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # If pursuer can capture next move (radius 0), strongly prefer it.
        capture = 1 if (dist == 0) else 0

        if is_pursuer:
            score = -dist
            if capture:
                score = 10_000 + capture * 100
        else:
            score = dist
            if capture:
                score = -10_000  # avoid immediate capture

        # Tie-breaker heuristic: keep moving toward the "best corner alignment"
        # to cope with wall runner evasion style.
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score and best is not None:
            # fixed dir order already provides determinism; keep earlier
            pass

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]