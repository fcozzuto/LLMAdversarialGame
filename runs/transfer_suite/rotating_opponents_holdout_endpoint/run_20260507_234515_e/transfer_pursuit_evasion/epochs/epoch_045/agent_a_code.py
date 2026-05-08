def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in oset
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "")

    if not self_is_pursuer:
        # Evader: maximize distance, then prefer moves that reduce own mobility (stay in safer pocket), avoid leaving grid.
        best = -10**9
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = md(nx, ny, ox, oy)
            score = d * 100 - mobility(nx, ny) * 1
            if score > best:
                best, best_move = score, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Pursuer: minimize distance; tie-break by reducing evader mobility; then move toward tighter/safer center-adjacent lines.
    best = 10**9
    best_move = (0, 0)
    opp_mob = mobility(ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = md(nx, ny, ox, oy)
        new_opp_mob = mobility(ox, oy)  # static approx (no capture radius); still use to break ties
        # Slight preference for moves that push relative position (toward evader axis) deterministically.
        dir_bonus = 0
        if nx != ox: dir_bonus += -1 if (nx - ox) * (sx - ox) < 0 else 0
        if ny != oy: dir_bonus += -1 if (ny - oy) * (sy - oy) < 0 else 0
        # Tie-breaking score: primary d, then minimize opponent mobility reachable from its current neighborhood,
        # then bias toward moves that reduce distance in a more direct (non-diagonal-only) way.
        score = (d * 1000) + (new_opp_mob * 10) + (1 if dx == 0 or dy == 0 else 0) + (-dir_bonus)
        if score < best or (score == best and (dx, dy) < best_move):
            best, best_move = score, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]