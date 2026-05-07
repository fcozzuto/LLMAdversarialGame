def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]
    moves.append((0, 0))

    best_move = (0, 0)
    best_key = (-10**18, -10**18, -10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Choose the resource that maximizes our relative closeness vs opponent.
        best_lead = -10**18
        best_self_dist = 10**18
        best_opp_dist = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd  # higher is better
            if lead > best_lead or (lead == best_lead and sd < best_self_dist):
                best_lead, best_self_dist, best_opp_dist = lead, sd, od

        # If opponent is closer everywhere (lead<=0), back off a bit while still improving own distance.
        opp_backoff = cheb(nx, ny, ox, oy)
        key = (best_lead, -best_self_dist, opp_backoff)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]