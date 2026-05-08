def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    self_role = str(observation.get("self_role", "")).lower()
    my_is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if my_is_pursuer:
        target = max(corners, key=lambda c: -dist(c[0], c[1], sx, sy))
        target = max(corners, key=lambda c: dist(c[0], c[1], sx, sy))
    else:
        target = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))

    best_dx, best_dy = 0, 0
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d_target = dist(nx, ny, target[0], target[1])
        d_opp = dist(nx, ny, ox, oy)
        score = d_opp if my_is_pursuer else -d_opp
        if my_is_pursuer:
            score = (-d_target, -d_opp)
        else:
            score = (d_target, -d_opp)
        if best_score is None:
            best_score = score
            best_dx, best_dy = dx, dy
        else:
            if score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]