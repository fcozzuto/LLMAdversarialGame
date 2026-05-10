def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def manhattan(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    # Precompute a few nearest unclaimed distances (cheap, deterministic)
    unclaimed_list = list(unclaimed)
    def nearest_unclaimed_dist2(x, y):
        best = 10**9
        # If unclaimed is empty, fall back to distance to our territory
        for tx, ty in unclaimed_list[:32]:
            d = manhattan(x, y, tx, ty)
            if d < best:
                best = d
                if best == 0:
                    break
        return best if best != 10**9 else 0

    # Also approximate "opponent pressure": distance to opponent territory cells if available
    opp_list = list(opp_terr)
    def nearest_opp_terr_dist(x, y):
        best = 10**9
        for tx, ty in opp_list[:32]:
            d = manhattan(x, y, tx, ty)
            if d < best:
                best = d
                if best == 0:
                    break
        return best if best != 10**9 else manhattan(x, y, ox, oy)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        score = 0
        if (nx, ny) in resources:
            score += 1200
        if (nx, ny) in unclaimed:
            score += 220
        if (nx, ny) in self_terr:
            score += 35
        if (nx, ny) in opp_terr:
            score += 140  # flipping is beneficial

        # Prefer moves that get closer to nearby unclaimed
        nd = nearest_unclaimed_dist2(nx, ny)
        score += 40 - 6 * nd

        # Prefer pushing away from the opponent's territory unless taking it directly
        od = nearest_opp_terr_dist(nx, ny)
        score += 0 if (nx, ny) in opp_terr else (12 - 2 * od)

        # Mild border bias to avoid getting boxed in
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            score += 6

        # Deterministic tie-break: fixed dir iteration already, but keep explicit
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]