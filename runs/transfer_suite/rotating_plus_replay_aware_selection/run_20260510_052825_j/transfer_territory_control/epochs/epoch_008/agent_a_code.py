def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_to_opp(cx, cy):
        cnt = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            nx, ny = cx + ddx, cy + ddy
            if (nx, ny) in oppT:
                cnt += 1
        return cnt

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0

        # Prefer immediate flips/steals.
        if (nx, ny) in oppT:
            score += 1000.0 + 10.0 * adj_to_opp(nx, ny)

        # Claim pressure cells: unclaimed that border opponent territory.
        if (nx, ny) in unclaimed:
            score += 120.0 * adj_to_opp(nx, ny)
            # Slightly prefer moving toward opponent to keep the edge contest.
            score += 6.0 / (1.0 + dist((nx, ny), (ox, oy)))

        # Avoid getting stuck away from the frontier: keep near opponent or expand.
        if (nx, ny) in selfT:
            score -= 2.0  # less valuable than taking territory
            score += 0.5 * adj_to_opp(nx, ny)

        # Basic proximity tie-break toward opponent and toward unclaimed.
        score += 1.5 / (1.0 + dist((nx, ny), (ox, oy)))
        score += 0.2 * (1 if (nx, ny) in unclaimed else 0)

        # Deterministic tie-breaking: lexicographic by (dx, dy).
        key = (score, -abs(dx) - abs(dy), -nx, -ny, dx, dy)
        if best is None or key > best:
            best = key
            best_score = score

    if best is None:
        return [0, 0]
    return [best[-2], best[-1]]