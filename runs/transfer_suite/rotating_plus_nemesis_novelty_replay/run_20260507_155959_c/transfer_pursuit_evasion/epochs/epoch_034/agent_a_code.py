def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")

    def score(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        if is_pursuer:
            # chase: minimize distance; slight preference for "toward" movement
            toward = abs(nx - ox) + abs(ny - oy)
            return -toward * 10 + (-d)
        else:
            # evade: maximize distance; prefer moving toward farthest corner from opponent
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_push = abs(far_corner[0] - nx) + abs(far_corner[1] - ny)
            return d * 10 + corner_push

    best = None
    bestv = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]