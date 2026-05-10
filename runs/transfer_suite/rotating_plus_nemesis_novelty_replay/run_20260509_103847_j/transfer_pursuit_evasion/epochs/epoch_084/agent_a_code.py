def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role)

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    if is_evader:
        best_score = -10**9
        # keep far from pursuer; also prefer moves with more freedom
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            d = manh(nx, ny, ox, oy)
            free = 0
            for adx, ady in deltas:
                tx, ty = nx + adx, ny + ady
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in blocked:
                    free += 1
            score = d * 10 + free
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        best_score = -10**9
        # chase opponent; prefer reducing distance and avoiding obstacles
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            d = manh(nx, ny, ox, oy)
            free = 0
            for adx, ady in deltas:
                tx, ty = nx + adx, ny + ady
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in blocked:
                    free += 1
            score = -d * 10 + free
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]