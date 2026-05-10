def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free_n(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        d = dist(nx, ny, ox, oy)
        if pursuer:
            # chase: reduce distance; prefer more freedom if tied
            val = (-d, free_n(nx, ny))
        else:
            # evade: increase distance; also prefer corners away from opponent
            corner_goal = (w - 1 if ox < w // 2 else 0, h - 1 if oy < h // 2 else 0)
            dc = dist(nx, ny, corner_goal[0], corner_goal[1])
            val = (d, dc, free_n(nx, ny))

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]