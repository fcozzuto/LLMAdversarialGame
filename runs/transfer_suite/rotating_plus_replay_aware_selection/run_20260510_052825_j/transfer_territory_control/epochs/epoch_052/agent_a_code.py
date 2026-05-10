def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick a deterministic best goal among a small prefix of sorted unclaimed.
    unclaimed_sorted = sorted(unclaimed)
    best_goal = (x, y)
    best_g = -10**18
    k = 18 if len(unclaimed_sorted) > 18 else len(unclaimed_sorted)
    for i in range(k):
        tx, ty = unclaimed_sorted[i]
        g = (dist(tx, ty, ox, oy) - dist(tx, ty, x, y))
        if (x == 0 and y == 0):
            g += 0.02 * (tx + ty)
        elif (x == w - 1 and y == h - 1):
            g += 0.02 * ((w - 1 - tx) + (h - 1 - ty))
        elif x == 0:
            g += 0.01 * (tx + (h - 1 - ty))
        elif y == 0:
            g += 0.01 * ((w - 1 - tx) + ty)
        if g > best_g:
            best_g = g
            best_goal = (tx, ty)

    best_move = [0, 0]
    best_s = -10**18
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    gx, gy = best_goal
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        step_state = 0
        if (nx, ny) in oppT:
            step_state += 6
        elif (nx, ny) in unclaimed:
            step_state += 3
        elif (nx, ny) in selfT:
            step_state += 1
        # Prefer moving closer to goal; also keep away from opponent if not attacking.
        toward = dist(nx, ny, gx, gy) - dist(x, y, gx, gy)
        away_from_opp = dist(nx, ny, ox, oy) - dist(x, y, ox, oy)
        s = step_state * 10 + (-toward) * 2 + away_from_opp * 0.15
        # If we can directly enter opponent territory, make it primary.
        if (nx, ny) in oppT:
            s += 100
        if s > best_s:
            best_s = s
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]