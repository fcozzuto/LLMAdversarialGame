def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def is_edge(x, y):
        return x == 0 or x == w - 1 or y == 0 or y == h - 1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9

    # Prefer targets we can reach first, and prefer non-edge cells against edge-patrol opponents.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if dx == 0 and dy == 0 and len(resources) > 1:
            # Mild discouragement of staying put
            base_stay = -1
        else:
            base_stay = 0

        step_score = base_stay
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            advantage = od - sd
            edge_pen = 3 if is_edge(rx, ry) else 0
            # If we're not keeping up, penalize more; if we are, reward faster capture.
            speed = 0
            if sd <= od:
                speed = 2 - (sd // 2)
            else:
                speed = -2 - ((sd - od) // 1)
            s = advantage - edge_pen + speed
            if s > step_score:
                step_score = s

        # Add small tie-break: move to increase our distance from opponent when possible
        step_score += (md(nx, ny, ox, oy) - md(sx, sy, ox, oy)) // 2

        if step_score > best_score:
            best_score = step_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]