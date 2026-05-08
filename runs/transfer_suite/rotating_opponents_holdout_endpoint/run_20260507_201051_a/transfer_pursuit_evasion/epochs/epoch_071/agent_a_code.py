def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    orr = str(observation.get("opponent_role") or "").lower()
    env = str(observation.get("environment_name") or "").lower()
    is_evader = ("evad" in sr) or ("escape" in sr) or ("runner" in sr) or ("evad" in orr) or ("escape" in orr) or ("runner" in orr)
    if "evasion" in env and not is_evader:
        is_evader = ("evad" in orr) or ("escape" in orr) or ("runner" in orr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    rsrc = observation.get("resources") or []
    for r in rsrc:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    target_list = res if res else [(ox, oy)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = min(cheb(nx, ny, tx, ty) for tx, ty in target_list)
        score = d if is_evader else -d
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]