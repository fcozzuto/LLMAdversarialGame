def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        ad = a - c
        bd = b - d
        if ad < 0:
            ad = -ad
        if bd < 0:
            bd = -bd
        return ad if ad > bd else bd

    moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        score = -d if pursuer else d
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]