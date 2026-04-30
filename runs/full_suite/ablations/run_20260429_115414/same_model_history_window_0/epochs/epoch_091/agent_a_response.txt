def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    # If no resources, drift toward center deterministically
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        cand = (dx, dy)
        nx, ny = sx + cand[0], sy + cand[1]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [cand[0], cand[1]]
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose resource with best relative advantage (self closer than opponent), tie-break by absolute distance.
    best = None
    for rx, ry in resources:
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        adv = d2 - d1  # higher is better
        score = (-adv, d1, abs(rx - sx), abs(ry - sy))  # minimize negative advantage first
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    (trg_x, trg_y) = best[1]

    desired_dx = 0 if sx == trg_x else (1 if sx < trg_x else -1)
    desired_dy = 0 if sy == trg_y else (1 if sy < trg_y else -1)

    # Try deterministic set of moves: desired, then axis moves, then diagonals, then stay.
    candidates = []
    candidates.append((desired_dx, desired_dy))
    # Axis nudges
    candidates.append((desired_dx, 0))
    candidates.append((0, desired_dy))
    # Diagonal alternatives
    candidates.append((desired_dx, -desired_dy))
    candidates.append((-desired_dx, desired_dy))
    # Small systematic fallback and stay
    candidates.append((0, 0))
    # Ensure uniqueness
    seen = set()
    ordered = []
    for c in candidates:
        if c not in seen:
            seen.add(c); ordered.append(c)

    def valid_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_key = None
    for dx, dy in ordered:
        if not valid_move(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d_to = dist((nx, ny), (trg_x, trg_y))
        d_opp = dist((ox, oy), (trg_x, trg_y))
        # Prefer reducing distance to target; if tie, prefer making us relatively closer than opponent.
        key = (d_to, -(d_opp - d_to), abs(nx - trg_x) + abs(ny - trg_y), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if not valid_move(best_move[0], best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]