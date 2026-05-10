def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("runner" in self_role)
    opp_is_evader = ("evader" in opp_role) or ("evasion" in opp_role) or ("runner" in opp_role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    chase = not self_is_evader and opp_is_evader
    if self_is_evader and not opp_is_evader:
        chase = False
    if self_role == "" and opp_role == "":
        chase = cheb(sx, sy, ox, oy) <= 2

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = cheb(nx, ny, ox, oy)
        v = d if not chase else -d
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            best = (dx, dy)
            bestv = v

    if best is None:
        return [0, 0]
    return [best[0], best[1]]