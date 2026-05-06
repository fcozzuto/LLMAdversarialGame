def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = (0, 0)
    best_score = -10**9

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        ns = (nx, ny)

        # Prefer resources where we will be closer than the opponent after our move, with extra caution near opponent lines.
        score = 0
        for r in resources:
            d_s = dist8(ns, r)
            d_o = dist8((ox, oy), r)
            if d_s == 0:
                score += 10000
                continue
            v = (d_o - d_s) * 50  # advantage over opponent
            # Denier behavior: avoid "obvious" resource lanes near their current x/y
            if r[0] == ox or r[1] == oy:
                v -= 120
            # Encourage progress even if we aren't ahead: closer is better
            v -= d_s * 2
            score += v

        # Small tie-break: don't give opponent free adjacency
        score -= (dist8((ox, oy), ns) == 0) * 500
        score -= (dist8((ox, oy), ns) == 1) * 80

        if score > best_score:
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]