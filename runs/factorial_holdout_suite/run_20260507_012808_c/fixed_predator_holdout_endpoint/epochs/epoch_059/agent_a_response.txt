def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in set(resources):
        return [0, 0]
    if not resources:
        return [0, 0]

    def king_dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Choose targets that are simultaneously good for us and bad for the opponent (denial).
    ranked = []
    for (rx, ry) in resources:
        sd = king_dist(rx, ry, sx, sy)
        od = king_dist(rx, ry, ox, oy)
        # favor: opponent farther than we are; tie-break: closer for us
        ranked.append((od - sd, -sd, rx, ry, sd, od))
    ranked.sort(reverse=True)
    top = ranked[:min(4, len(ranked))]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Materially different: score by "next-step advantage over multiple targets",
        # emphasizing resources the opponent is unlikely to reach first.
        score = 0
        for i, item in enumerate(top):
            rx, ry, sd0 = item[2], item[3], item[4]
            # recompute from next position
            sd = king_dist(rx, ry, nx, ny)
            od = king_dist(rx, ry, ox, oy)
            adv = od - sd
            # small reward for immediate progress, stronger reward for winning denial race
            score += (adv * 10) + (max(0, 7 - sd) if adv >= 0 else -sd)
            if i == 0:
                score += 25 if adv >= 0 else -10

        # additional obstacle-aware preference: move that doesn't worsen distance to the best target
        brx, bry = top[0][2], top[0][3]
        sd_now = king_dist(brx, bry, sx, sy)
        sd_next = king_dist(brx, bry, nx, ny)
        score += 3 if sd_next <= sd_now else -2

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]