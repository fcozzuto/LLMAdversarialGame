def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    role_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("chaser" in self_role)
    if not role_pursuer and (("pursuer" in opp_role) or ("pursuit" in opp_role) or ("chaser" in opp_role)):
        role_pursuer = False
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist2(x, y, px, py):
        dx, dy = x - px, y - py
        return dx * dx + dy * dy

    def free_degree(x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        fd = free_degree(nx, ny)
        if role_pursuer:
            key = (-d, -fd, dx, dy)  # smaller distance preferred => maximize -d
        else:
            key = (d, -fd, dx, dy)   # larger distance preferred => maximize d
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    if best is None:
        return [0, 0]
    return best[1]