def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role") or "")
    pursuer = ("purs" in role.lower()) or (role.lower() == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def edge_bias(x, y):
        # prefer staying away from opponent's cornering by slightly favoring far edges when evading
        dL = x
        dR = (w - 1) - x
        dB = y
        dT = (h - 1) - y
        return min(dL, dR, dB, dT)

    best = None
    best_score = None
    # determinism: fixed preference order already in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny)
        # pursuer: minimize distance; evader: maximize distance
        score = (-d if pursuer else d)
        # small tie-breakers to reduce dithering
        if pursuer:
            # encourage tightening by pushing toward nearest edge towards opponent when possible
            score += 0.02 * edge_bias(nx, ny)
            # discourage stepping into immediate dead zones: count available next moves
            avail = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty):
                    avail += 1
            score += 0.01 * avail
        else:
            # evader: further bias toward edges far from pursuer
            score += 0.03 * edge_bias(nx, ny)
            # discourage moves that reduce mobility too much
            avail = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty):
                    avail += 1
            score += 0.005 * avail
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]