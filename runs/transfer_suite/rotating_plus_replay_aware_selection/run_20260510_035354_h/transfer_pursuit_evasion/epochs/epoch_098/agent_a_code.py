def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    s = (self_role + " " + opp_role).lower()
    pursue = ("pursuer" in self_role.lower()) or ("pursuer" in s and "evader" not in self_role.lower())

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def neighbors_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    cur_dist = abs(sx - ox) + abs(sy - oy)
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        dist = abs(nx - ox) + abs(ny - oy)
        progress = cur_dist - dist
        center = abs(nx - cx) + abs(ny - cy)
        neigh = neighbors_count(nx, ny)

        if pursue:
            # minimize distance, prefer progress, avoid cramped cells, slight preference toward center
            val = (-dist * 2.0) + (progress * 1.2) + (neigh * 0.35) + (-center * 0.03)
        else:
            # evade: maximize distance, prefer negative progress, avoid being cornered (more free moves), slight bias to center
            val = (dist * 2.0) + (-progress * 1.2) + (neigh * 0.35) + (-center * 0.03)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move