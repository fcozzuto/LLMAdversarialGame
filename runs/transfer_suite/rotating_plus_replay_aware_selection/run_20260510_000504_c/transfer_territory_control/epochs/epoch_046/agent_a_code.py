def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def nearest_target_dist(x, y):
        if unclaimed:
            best = 10**9
            for tx, ty in list(unclaimed)[:32]:
                d = manh(x, y, tx, ty)
                if d < best:
                    best = d
                    if best == 0:
                        return 0
            return best
        if resources:
            best = 10**9
            for tx, ty in list(resources)[:16]:
                d = manh(x, y, tx, ty)
                if d < best:
                    best = d
                    if best == 0:
                        return 0
            return best
        return 0

    # Prefer claiming near the frontier and opportunistic flips of opponent territory.
    best_score = -10**18
    best_move = (0, 0)
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_terr:
            score += 6
        elif (nx, ny) in unclaimed:
            score += 18
        elif (nx, ny) in opp_terr:
            score += 22

        # Reduce distance to nearest unclaimed/resources.
        score += -2.2 * nearest_target_dist(nx, ny)

        # Slightly bias toward center (helps vs center-claimers once frontier is open).
        score += -0.05 * manh(nx, ny, int(center_x), int(center_y))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]