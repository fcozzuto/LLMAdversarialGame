def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((x, y))
        except:
            pass
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def legal(x, y):
        return inb(x, y) and (x, y) not in obs
    def d(x, y):
        return max(abs(x - ox), abs(y - oy))
    role = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in role)
    opp_pursuer = ("pursuer" in orole)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            return [dx, dy]
        dist = d(nx, ny)
        if pursuer:
            k = (0, dist)
        else:
            k = (1, -dist)
        # If opponent is also pursuer, prefer moves that increase our distance more deterministically.
        if opp_pursuer and pursuer:
            k = (0, dist * 2)
        # Tie-break deterministically by move order (dx,dy)
        key = (k[0], k[1], abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best