def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    evading = any(k in role for k in ("evade", "runner", "flee", "evasion", "evader"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def obst_cost(x, y):
        if (x, y) in obstacles:
            return 10**7
        cost = 0
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d == 0:
                return 10**7
            if d == 1:
                cost += 50
            elif d == 2:
                cost += 16
            elif d == 3:
                cost += 7
            elif d <= 4:
                cost += 3
        return cost

    def edge_preference(x, y):
        # Deterministic: evader prefers staying near far corners/edges; pursuer prefers closer to opponent by edge bias.
        dedge = min(x, w - 1 - x, y, h - 1 - y)
        # Smaller dedge means more "edge"; convert to a preference term.
        return (dedge - 1.5) * (-1 if evading else 1)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = cheb(nx, ny)
        c = obst_cost(nx, ny)
        if evading:
            # Maximize distance, lightly penalize obstacles, and prefer dispersal from opponent.
            score = dist * 1000 - c + edge_preference(nx, ny) - (abs(ox - nx) + abs(oy - ny)) * 0.5
        else:
            # Minimize distance to opponent, avoid obstacles.
            score = -dist * 1000 - c + edge_preference(nx, ny) + (abs(ox - nx) + abs(oy - ny)) * 0.1

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]