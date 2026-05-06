def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def steps(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def interior(x, y):
        dleft = x
        dright = w - 1 - x
        ddown = y
        dup = h - 1 - y
        m = dleft if dleft < dright else dright
        m = m if m < ddown else ddown
        m = m if m < dup else dup
        return m

    best_move = (0, 0)
    best_score = None
    center = (w - 1) // 2
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_near_bonus = 0
        score = -10**9
        for rx, ry in resources:
            ms = steps(nx, ny, rx, ry)
            os_ = steps(ox, oy, rx, ry)
            adv = os_ - ms  # higher is better (we are closer than opponent)
            # Encourage taking resources that are more central to reduce opponent edge probing
            cen_bias = interior(rx, ry) - (abs(rx - center) + abs(ry - center)) * 0.15
            # Favor immediate progress to high-advantage targets
            val = adv * 3.0 - ms + cen_bias
            if val > score:
                score = val
                my_near_bonus = ms
        # Small tie-break: prefer staying away from edges and not oscillating unnecessarily
        tie = interior(nx, ny) * 0.01 - (abs(dx) + abs(dy)) * 0.001
        score += tie
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]