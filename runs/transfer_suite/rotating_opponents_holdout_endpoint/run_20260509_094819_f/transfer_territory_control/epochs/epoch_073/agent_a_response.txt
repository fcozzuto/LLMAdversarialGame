def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Anchor: nearest meaningful target cell
    targets = list(unclaimed) if unclaimed else list(opp_t) if opp_t else [(ox, oy)]
    tx, ty = min(targets, key=lambda c: (dist((sx, sy), c), c[0], c[1]))

    # Bias toward opponent to keep pressure
    bx = 1 if ox > sx else (-1 if ox < sx else 0)
    by = 1 if oy > sy else (-1 if oy < sy else 0)

    best = (None, None)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 5
        elif (nx, ny) in opp_t:
            score += 3
        elif (nx, ny) in self_t:
            score += 1

        # Move closer to target; prefer moves that also head toward opponent
        score += -dist((nx, ny), (tx, ty))
        score += 0.5 * ((bx != 0 and dx == bx) + (by != 0 and dy == by))

        # Avoid stagnation if possible
        if dx == 0 and dy == 0:
            score -= 0.25

        # Deterministic tie-break via move order
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best[0] is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]