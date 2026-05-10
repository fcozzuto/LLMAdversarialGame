def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in role) or (("pursuer" in opp_role) and ("evader" not in role))
    if ("evader" in role) and ("pursuer" not in role):
        pursuer = False

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def corner_min_dist(x, y):
        best = 10**9
        for cx, cy in corners:
            d = cheb(cx, cy, x, y)
            if d < best:
                best = d
        return best

    best_score = None
    best_delta = (0, 0)
    sign = -1 if pursuer else 1  # pursuer: minimize distance => negative cheb
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, ox, oy)
        cdist = corner_min_dist(nx, ny)
        # deterministic tie-breaking: fixed move order handles equal scores
        score = sign * dist
        # extra bias: evader prefer corners (increase cdist penalty => smaller value better for pursuer/evader differently)
        if pursuer:
            score += -0.01 * cdist + (0.001 if (dx, dy) != (0, 0) else 0.0)
        else:
            score += 0.01 * (-cdist) + (0.001 if (dx, dy) != (0, 0) else 0.0)
        if best_score is None or score > best_score:
            best_score = score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]