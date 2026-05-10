def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "pursuer")).lower()
    pursuer = role != "evader"

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_target = corners[0]
    best_corner_dist = -1
    for cx, cy in corners:
        if valid(cx, cy):
            d = cheb(cx, cy, ox, oy)
            if d > best_corner_dist:
                best_corner_dist = d
                best_target = (cx, cy)

    target = (ox, oy) if pursuer else best_target

    best_score = -10**18 if not pursuer else 10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if pursuer:
            dist_to_opp = cheb(nx, ny, ox, oy)
            score = dist_to_opp
            if (nx, ny) == (ox, oy):
                score = -10**12
            if score < best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            dist_to_opp = cheb(nx, ny, ox, oy)
            dist_to_target = cheb(nx, ny, target[0], target[1])
            score = (-dist_to_opp, dist_to_target)  # lexicographic via tuple comparisons
            if best_move == [0, 0] and best_score == -10**18:
                best_score = score
                best_move = [dx, dy]
            else:
                if score > best_score:
                    best_score = score
                    best_move = [dx, dy]

    if best_move == [0, 0]:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
    return [int(best_move[0]), int(best_move[1])]