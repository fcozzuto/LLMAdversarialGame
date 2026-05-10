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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        ad = a - c
        bd = b - d
        ad = ad if ad >= 0 else -ad
        bd = bd if bd >= 0 else -bd
        return ad if ad > bd else bd

    # Deterministic tie-breaker preference order
    pref = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    pref_index = {m: i for i, m in enumerate(pref)}

    best = None
    best_val = None
    for dx, dy in pref:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # pursuer wants smaller distance; evader wants larger distance
        val = -d if pursuer else d
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]