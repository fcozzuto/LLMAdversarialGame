def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    # Candidates: unclaimed cells adjacent to opponent territory (likely sweep frontier)
    candidates = []
    for (x, y) in unclaimed:
        near_opp = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    near_opp = True
                    break
            if near_opp:
                break
        if near_opp:
            candidates.append((x, y))

    if not candidates:
        candidates = list(unclaimed)
        if not candidates:
            return [0, 0]

    # Pick deterministic target: minimize own distance, tie-break by maximize closeness advantage over opponent
    opppos = (ox, oy)
    selfpos = (sx, sy)
    best = None
    best_key = None
    for c in candidates:
        dS = dist(selfpos, c)
        dO = dist(opppos, c)
        key = (dS, -dO, c[0], c[1])
        if best_key is None or key < best_key:
            best_key = key
            best = c
    tx, ty = best

    # Evaluate possible moves with obstacle avoidance and immediate territory gain
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        next_cell = (nx, ny)
        score = 0.0
        if next_cell in opp_terr:
            score += 1000.0
        elif next_cell in unclaimed:
            score += 200.0
        elif next_cell in self_terr:
            score += 20.0
        # Drift toward target; slight bias to cut distance to opponent as contest pressure
        score -= 3.0 * dist((nx, ny), (tx, ty))
        score -= 0.3 * dist((nx, ny), (ox, oy))
        # Deterministic tie-break
        key = (-score, dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]