def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Targeting score: aggressively take unclaimed, then invade opponent, avoid moving toward opponent too easily.
    best = None
    for dx, dy, nx, ny in valid:
        p = 0
        if (nx, ny) in oppT:
            p += 6
        elif (nx, ny) in unclaimed:
            p += 4
        elif (nx, ny) in selfT:
            p += 1
        else:
            p += 1

        # Prefer expanding into regions near unclaimed/opponent boundary.
        if unclaimed:
            mind = 10**9
            for tx, ty in ((nx, ny - 1), (nx, ny + 1), (nx - 1, ny), (nx + 1, ny), (nx - 1, ny - 1), (nx + 1, ny + 1), (nx - 1, ny + 1), (nx + 1, ny - 1)):
                if (0 <= tx < w and 0 <= ty < h) and (tx, ty) in unclaimed:
                    mind = 0
                    break
            if mind != 0:
                # cheap directional bias: move closer to nearest unclaimed if it exists nearby
                p += -0.5 * min(dist((nx, ny), c) for c in unclaimed if abs(c[0]-nx)+abs(c[1]-ny) <= 3) if any(abs(c[0]-nx)+abs(c[1]-ny) <= 3 for c in unclaimed) else 0
        if oppT:
            # If close to opponent territory, prioritize contact/invasion
            near_opp = False
            for tx, ty in ((nx, ny - 1), (nx, ny + 1), (nx - 1, ny), (nx + 1, ny), (nx - 1, ny - 1), (nx + 1, ny + 1), (nx - 1, ny + 1), (nx + 1, ny - 1)):
                if (0 <= tx < w and 0 <= ty < h) and (tx, ty) in oppT:
                    near_opp = True
                    break
            if near_opp:
                p += 2

        # Anti-stall: prefer increasing Chebyshev distance from self boundary toward frontier direction
        p += -0.05 * dist((nx, ny), (ox, oy))  # don't run directly into opponent unless invading

        # Tie-break deterministically by move ordering preference: rightward, then upward-ish, then staying.
        tie = (-(dx == 1), -(dy == -1), -(dx == 0 and dy == 0), dx, dy)

        key = (p,) + tie
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]