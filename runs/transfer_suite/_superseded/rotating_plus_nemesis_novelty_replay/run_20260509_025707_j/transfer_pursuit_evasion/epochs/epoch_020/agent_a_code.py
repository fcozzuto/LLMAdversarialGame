def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if w < 1 or h < 1 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
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

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        if not obstacles:
            return 0
        p = 0
        for ox2, oy2 in obstacles:
            d = abs(x - ox2) + abs(y - oy2)
            if d == 0:
                return 10**9
            if d == 1:
                p += 6
            elif d == 2:
                p += 2
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_now = cheb(nx, ny, ox, oy)
        d_threat = obs_pen(nx, ny)
        # pursuer: minimize distance; evader: maximize distance
        # add obstacle-aware term: pursuer avoids obstacles strongly, evader mildly avoids being near obstacles
        if is_evader:
            val = -(d_now * 100) + d_threat * 3
        else:
            val = d_now * 100 + d_threat * 5
        if best_val is None or (val < best_val if not is_evader else val < best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]