def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    # Candidate deltas in deterministic priority order (stay, then closer diagonals)
    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target resource where we are at least as close as opponent if possible
    my = (sx, sy)
    opp = (ox, oy)
    best = None
    best_key = None
    for r in resources:
        myd = dist(my, r)
        opd = dist(opp, r)
        # prefer resources we can reach not worse than opponent; then minimize my distance
        key = (0, myd) if myd <= opd else (1, myd - opd, myd)
        if best is None or key < best_key:
            best = r
            best_key = key
    if best is None:
        # No resources known: move toward opponent to potentially deny
        target = (ox, oy)
    else:
        target = best

    # Evaluate moves: minimize distance to target; keep away from obstacles; mild preference to move away from opponent if tied
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = abs(nx - target[0]) + abs(ny - target[1])
        opd = abs(nx - ox) + abs(ny - oy)
        # Higher is better; use integers only
        score = (-myd * 1000) + (opd * 3)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]