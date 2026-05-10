def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    valid_res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not valid_res:
        return [0, 0]

    rem = observation.get("remaining_resource_count", len(valid_res))
    best = None
    for rx, ry in valid_res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer cells opponent is farther from; when late, prioritize closeness.
        score = (od - sd) * (1.2 if rem > 5 else 0.4) - (0.9 if rem <= 3 else 0.2) * sd
        # Slightly avoid targets that are "too easy" for opponent if adjacent line sweep.
        if abs(rx - ox) <= 1 and ry == oy:
            score -= 0.6
        if abs(ry - oy) <= 1 and rx == ox:
            score -= 0.4
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Greedy toward target; prefer moves that reduce opponent's advantage.
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # Encourage stepping closer and discourage wasting by staying too far.
        val = (od2 - sd2) - 0.03 * (abs(dx) + abs(dy))
        # If current move is away from target, penalize more.
        curd = man(sx, sy, tx, ty)
        if sd2 > curd:
            val -= 0.5
        # Avoid moving into a square immediately adjacent to many obstacles (micro-dodge).
        near_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                x2, y2 = nx + adx, ny + ady
                if inb(x2, y2) and (x2, y2) in obstacles:
                    near_obs += 1
        val -= 0.08 * near_obs

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move