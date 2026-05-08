def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    if not resources:
        return [0, 0]

    def king_dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored_moves = []

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        best = -10**18
        for rx, ry in resources:
            t_us = king_dist(nx, ny, rx, ry)
            t_op = king_dist(ox, oy, rx, ry)
            # Prefer reaching sooner; strongly prefer resources where we're not slower than opponent.
            # Penalize approaching "contested" resources.
            score = (300.0 / (t_us + 1.0)) - (250.0 / (t_op + 1.0))
            # Mild preference for closer absolute target (reduces thrashing).
            score += 0.5 / (king_dist(nx, ny, 0, 0) + 1.0)  # deterministic tie-break signal
            # If we can get there same/earlier, boost; if later, reduce.
            if t_us <= t_op:
                score += 60.0 / (t_us + 1.0)
            else:
                score -= 70.0 / (t_op + 1.0)
            if score > best:
                best = score
        scored_moves.append((best, dx, dy))

    scored_moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(scored_moves[0][1]), int(scored_moves[0][2])]