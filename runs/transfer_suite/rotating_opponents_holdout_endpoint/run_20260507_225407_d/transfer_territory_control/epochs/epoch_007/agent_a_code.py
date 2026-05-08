def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        if cell in opp_cells:
            base = 500.0
        elif cell in unclaimed:
            base = 120.0
        elif cell in self_cells:
            base = 20.0
        else:
            base = 0.0

        # Prefer moves that get closer to unclaimed; otherwise steer toward center.
        if unclaimed:
            # Deterministic: pick nearest unclaimed by Manhattan; tie by coord.
            tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - nx) + abs(p[1] - ny), p[0], p[1]))
            dist = abs(tx - nx) + abs(ty - ny)
            steer = 50.0 / (1 + dist)
        else:
            distc = abs(nx - cx) + abs(ny - cy)
            steer = 10.0 / (1 + distc)

        # Small penalty for staying still unless it's already beneficial.
        stay_pen = 2.0 if (dx == 0 and dy == 0 and base < 20.0) else 0.0

        score = base + steer - stay_pen
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move