def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    # Decide whether to "race" or "counter-deny":
    # if opponent is ahead to most resources, prioritize resources we are closer to.
    ahead_count = 0
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if dist(ox, oy, rx, ry) <= dist(sx, sy, rx, ry):
            ahead_count += 1
    counter_mode = ahead_count > (len(resources) // 2)

    best = None
    for dx, dy, nx, ny in legal:
        cell_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Favor resources we can secure sooner; in counter_mode, heavily penalize those opponent can take first.
            if counter_mode:
                secure = sd <= od
                score = (1 if secure else 0, od - sd, -sd, -abs(rx - ox) - abs(ry - oy), rx, ry)
            else:
                score = (0, od - sd, -sd, rx, ry) if sd <= od else (-1, od - sd, -sd, rx, ry)
            if cell_best is None or score > cell_best:
                cell_best = score
        if best is None or cell_best > best[0]:
            best = (cell_best, dx, dy)

    return [int(best[1]), int(best[2])]