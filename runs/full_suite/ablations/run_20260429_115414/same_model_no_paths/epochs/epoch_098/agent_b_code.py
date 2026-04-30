def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cd(a, b):
        # Chebyshev distance (diagonal moves allowed)
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a resource where we have temporal advantage: maximize (opp_dist - self_dist)
    best = None
    best_score = None
    for r in resources:
        sd = cd((sx, sy), r)
        od = cd((ox, oy), r)
        score = (od - sd, -sd)  # prefer bigger lead, then closer
        if best is None or score > best_score:
            best, best_score = r, score

    tx, ty = best
    self_dist = cd((sx, sy), best)
    opp_dist = cd((ox, oy), best)

    # If behind, defend by increasing distance from opponent (while not stepping into obstacles).
    # If ahead, advance toward target.
    target_mode = "advance" if self_dist <= opp_dist else "defend"

    # Deterministic tie-breaking via fixed delta order.
    chosen = (0, 0)
    chosen_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if target_mode == "advance":
            val = (-cd((nx, ny), (tx, ty)), -cd((nx, ny), (ox, oy)))  # closer to target, also farther from opponent
        else:
            val = (cd((nx, ny), (ox, oy)), -cd((nx, ny), (tx, ty)))  # farther from opponent, keep some pressure
        if chosen_val is None or val > chosen_val:
            chosen_val = val
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]