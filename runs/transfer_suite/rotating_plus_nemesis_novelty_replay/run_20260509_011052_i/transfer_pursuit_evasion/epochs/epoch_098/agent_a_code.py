def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        w = int(w)
        h = int(h)
        sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    except:
        w = 8; h = 8; sx = 0; sy = 0; ox = 0; oy = 0

    role = str(observation.get("self_role", "")).lower()
    evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
        except:
            x = p.get("x") if isinstance(p, dict) else None
            y = p.get("y") if isinstance(p, dict) else None
        if x is None or y is None:
            continue
        try:
            obs.add((int(x), int(y)))
        except:
            pass

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_val = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = abs(nx - ox)
        e = abs(ny - oy)
        cheb = d if d > e else e
        val = cheb if evader else -cheb
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]