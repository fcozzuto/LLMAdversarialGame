def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    if (sx, sy) in set(resources):
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**9)

    res_list = resources
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_pos = (nx, ny)

        # Evaluate how strongly we can secure nearby resources earlier than opponent.
        score = 0
        close_terms = 0
        for r in res_list:
            dm = dist(my_pos, r)
            do = dist((ox, oy), r)
            # If we can reach sooner, reward; if opponent can, penalize more when close.
            delta = do - dm
            if dm == 0:
                score += 1000
            else:
                if dm <= 3:
                    score += 20 * delta - dm
                    close_terms += 1
                else:
                    # still consider but less
                    score += 3 * delta - (dm // 2)

        # Slight preference to move closer to opponent to deny timing windows.
        score += -0.5 * dist(my_pos, (ox, oy))

        # Deterministic tie-break using move order.
        if score > best[1]:
            best = ((dx, dy), score)

    return [int(best[0][0]), int(best[0][1])]