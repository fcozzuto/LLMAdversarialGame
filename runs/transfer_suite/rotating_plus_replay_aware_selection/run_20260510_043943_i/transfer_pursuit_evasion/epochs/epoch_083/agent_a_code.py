def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    def obstacle_risk(nx, ny):
        if not obstacles:
            return 0
        risk = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 0:
                return 1000
            if d == 1:
                risk += 6
            elif d == 2:
                risk += 2
        return risk

    best_score = -10**9
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self_to_opp = cheb(nx, ny, ox, oy)
        risk = obstacle_risk(nx, ny)

        if pursuer:
            # Maximize: decrease distance to opponent, avoid obstacles.
            score = (-d_self_to_opp * 10) - risk
            # If can directly capture (radius 0: exact position), prioritize.
            if nx == ox and ny == oy:
                score += 2000
        else:
            # Evader: maximize distance from pursuer, and drift toward farthest corner.
            d_to_corner = cheb(nx, ny, far_corner[0], far_corner[1])
            score = (d_self_to_opp * 10) + (d_to_corner * 2) - risk

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move