def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_turns = int(observation.get("turns_remaining", 0) or 0)
    risk_gain = 2 if my_turns < 20 else 1

    best = None
    best_key = None
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = (do - dm) * risk_gain
        key = (lead, -dm, -((rx + ry) % 2), rx, ry)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best
    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    candidates.append((step_dx, step_dy))
    if step_dx != 0: candidates.append((step_dx, 0))
    if step_dy != 0: candidates.append((0, step_dy))
    if step_dx != 0 and step_dy != 0:
        candidates.append((step_dx, -step_dy))
        candidates.append((-step_dx, step_dy))
    candidates.append((0, 0))

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]

    return [0, 0]