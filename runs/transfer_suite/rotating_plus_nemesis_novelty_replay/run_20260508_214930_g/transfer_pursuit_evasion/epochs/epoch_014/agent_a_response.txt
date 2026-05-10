def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                obs.add((int(b[0]), int(b[1])))
            except:
                pass

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def move_from(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            return x, y
        return nx, ny
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role)

    def opponent_step(tsx, tsy):
        # predict opponent greedy move given its likely role against us
        # if we are pursuer, opponent is evader -> maximize distance
        # if we are evader, opponent is pursuer -> minimize distance
        best = (ox, oy)
        best_val = None
        for dx, dy in actions:
            nx, ny = move_from(ox, oy, dx, dy)
            d = dist2(nx, ny, tsx, tsy)
            val = d if (not pursuer) else -d
            if best_val is None or val > best_val:
                best_val = val
                best = (nx, ny)
        return best

    best_move = (0, 0)
    best_score = None

    for dx, dy in actions:
        nx, ny = move_from(sx, sy, dx, dy)
        if pursuer:
            # maximize capture (min distance), and keep movement toward opponent
            d = dist2(nx, ny, ox, oy)
            score = -d
            if nx == ox and ny == oy:
                score += 1000000
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # evader: predict pursuer step and maximize resulting distance
            nx2, ny2 = opponent_step(nx, ny)
            d_after = dist2(nx2, ny2, nx, ny)
            score = d_after
            # slight bias to stay away from edges
            score += 0.01 * (nx + (w - 1 - nx) + ny + (h - 1 - ny))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]