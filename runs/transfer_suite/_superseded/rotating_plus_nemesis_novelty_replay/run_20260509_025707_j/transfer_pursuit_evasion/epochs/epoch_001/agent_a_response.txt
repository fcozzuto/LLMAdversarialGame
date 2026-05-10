def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_role = observation.get("self_role", "")
    # dx,dy in {-1,0,1}
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Corner targets for evasion
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # For deterministic tie-breaking: fixed order over corners and moves
    def dist2(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    is_pursuer = ("pursuer" in self_role.lower()) or ("pursuit" in self_role.lower())
    target = (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if is_pursuer:
            # Chase: minimize distance to opponent, lightly prefer moves that reduce Manhattan too
            s1 = -dist2((nx, ny), target)
            s2 = -(abs(nx - ox) + abs(ny - oy))
            score = (s1 * 1000) + s2
        else:
            # Evade: maximize distance from pursuer; also bias toward farthest corner
            farthest_corner = max(corners, key=lambda c: dist2(c, target))
            s1 = dist2((nx, ny), target)
            s2 = dist2((nx, ny), farthest_corner)
            # Avoid getting stuck behind obstacles by penalizing proximity to obstacles
            prox = 0
            for ex, ey in obstacles:
                dd = abs(nx - ex) + abs(ny - ey)
                if dd == 0:
                    prox += 1000
                elif dd == 1:
                    prox += 3
                elif dd == 2:
                    prox += 1
            score = (s1 * 1000) + s2 - prox
        if best is None or (score > best_score):
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]