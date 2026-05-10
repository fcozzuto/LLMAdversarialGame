def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "guard", "pursuit")) or ("evader" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if sx == ox and sy == oy:
        return [0, 0]

    def manh(x, y): 
        return abs(x - ox) + abs(y - oy)

    best = None
    best_key = None
    # deterministic tie-break uses move order (already fixed); include secondary preference for diagonal when available
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manh(nx, ny)
        if pursuer:
            # primary: minimize distance to opponent
            # secondary: prefer diagonal (reduce both axes), then reduce x, then reduce y
            diag = 1 if (dx != 0 and dy != 0) else 0
            key = (d, -diag, nx, ny)
        else:
            # primary: maximize distance from opponent
            # secondary: prefer diagonal (increase both axes), then push toward farthest corner in x,y direction
            diag = 1 if (dx != 0 and dy != 0) else 0
            # farthest corner is opposite of opponent relative position
            tx = 0 if ox > (w - 1) // 2 else (w - 1)
            ty = 0 if oy > (h - 1) // 2 else (h - 1)
            corner_dist = abs(tx - nx) + abs(ty - ny)
            key = (-d, -diag, -corner_dist, -nx, -ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]