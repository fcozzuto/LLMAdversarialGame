def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("chase" in srole) or ("seeker" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in oset

    moves = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]

    def dist_cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def min_obs_clear(x, y):
        if not oset:
            return 999
        md = 999
        for (px, py) in oset:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not legal(nx, ny):
            continue
        d = dist_cheb(nx, ny)
        clear = min_obs_clear(nx, ny)
        # deterministic scoring; higher is better
        if is_pursuer:
            score = (-d) + 0.08 * clear
        else:
            score = (d) - 0.12 * (1 if clear == 999 else (8 - min(clear, 8)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]