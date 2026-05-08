def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    targets = list(unclaimed) if unclaimed else (list(opp_terr) if opp_terr else [(ox, oy)])
    tx, ty = targets[0]
    best_t = 10**9
    for t in targets:
        x, y = t
        d = abs(x - sx) + abs(y - sy)
        if d < best_t or (d == best_t and (y, x) < (ty, tx)):
            best_t, tx, ty = d, x, y

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0

        if cell in opp_terr:
            score += 12
        elif cell in unclaimed:
            score += 6
        elif cell in self_terr:
            score += 2

        score += -1.2 * (abs(nx - tx) + abs(ny - ty))

        # Slight preference for progressing toward opponent when no clear target
        if (not unclaimed) and (not opp_terr):
            score += -0.3 * (abs(nx - ox) + abs(ny - oy))

        # Deterministic tie-break
        score += -0.001 * (ny * w + nx)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]