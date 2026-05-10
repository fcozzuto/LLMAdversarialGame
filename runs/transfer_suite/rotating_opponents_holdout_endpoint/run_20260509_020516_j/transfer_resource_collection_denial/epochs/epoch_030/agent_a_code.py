def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", None) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def steps_dist(a, b):
        # Chebyshev gives best for king moves (diagonal allowed)
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # If no visible resources, shrink opponent distance deterministically.
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Opportunistic but defensive: prefer a resource we can arrive at earlier than opponent.
        # Score by lead (opp_dist - self_dist), then by absolute progress (self_dist smaller), then bias away from being trapped.
        local_best = -10**9
        for rx, ry in resources:
            sdist = steps_dist((nx, ny), (rx, ry))
            odist = steps_dist((ox, oy), (rx, ry))
            lead = odist - sdist
            # If opponent can take it sooner/equal, penalize heavily.
            if lead < 0:
                lead *= 2
            score = lead * 100 - sdist * 3 + (rx - nx == 0 and ry - ny == 0) * 50
            if score > local_best:
                local_best = score

        # Additional tie-breaker: avoid moves that let opponent immediately be adjacent to our chosen next-cell corridor.
        # (Simple heuristic: reduce moves that decrease distance to opponent.)
        opp_delta = steps_dist((ox, oy), (nx, ny)) - steps_dist((ox, oy), (sx, sy))
        local_score = local_best - opp_delta * 5

        if local_score > best_score:
            best_score = local_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]