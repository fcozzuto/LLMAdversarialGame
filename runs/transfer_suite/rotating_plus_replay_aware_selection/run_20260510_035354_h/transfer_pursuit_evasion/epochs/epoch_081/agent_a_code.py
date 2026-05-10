def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    parity = int(observation.get("turn_index", 0) or 0) & 1

    def min_obstacle_dist(x, y):
        md = 10**9
        for (ax, ay) in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md if obstacles else 10

    best = None
    best_score = None

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        sq = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        od = min_obstacle_dist(nx, ny)

        if evader:
            score = (dist * 1000) + (od * 5) + (sq)
        else:
            score = (-dist * 1000) + (od * 5) - sq

        # deterministic tie-break: prefer "keep moving" aligned with vector on even parity
        align = (dx != 0 or dy != 0)
        score += (1 if align else 0) * (3 if parity == 0 else 1)
        score += (-(abs(dx) + abs(dy))) * (0.1)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score and best is not None:
            # stable lexicographic tiebreak
            if [dx, dy] < best:
                best = [dx, dy]

    return best if best is not None else [0, 0]