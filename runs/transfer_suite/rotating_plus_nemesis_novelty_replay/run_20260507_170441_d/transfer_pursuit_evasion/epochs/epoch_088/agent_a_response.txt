def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None  # (score, -dxAbs, -dyAbs, dx, dy)
    ti = int(observation.get("turn_index", 0) or 0)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist = md(nx, ny, ox, oy)
        if is_evader:
            score = dist
            bias = ((dx * 3 + dy * 5 + ti) % 7) * 1e-6
            score = score + bias
            key = (score, -abs(dx), -abs(dy), dx, dy)
        else:
            score = -dist
            bias = ((-dx * 3 + -dy * 5 + ti) % 7) * 1e-6
            score = score + bias
            key = (score, -abs(dx), -abs(dy), dx, dy)
        if best is None or key > best:
            best = key

    return [best[3], best[4]]