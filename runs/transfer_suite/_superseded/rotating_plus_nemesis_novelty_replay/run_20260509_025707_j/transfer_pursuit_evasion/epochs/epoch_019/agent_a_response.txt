def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if w <= 0 or h <= 0 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y, a, b):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def obs_penalty(x, y):
        if not obstacles:
            return 0
        p = 0
        for (ox2, oy2) in obstacles:
            d = abs(x - ox2) + abs(y - oy2)
            if d == 0:
                return 10**6
            if d == 1:
                p += 6
            elif d == 2:
                p += 3
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    if is_evader:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            m = manh(nx, ny, ox, oy)
            score = (d * 1000 + m) - obs_penalty(nx, ny)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    else:
        best_score = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            m = manh(nx, ny, ox, oy)
            score = (d * 1000 + m) + obs_penalty(nx, ny)
            if score < best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]