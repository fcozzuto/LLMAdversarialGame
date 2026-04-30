def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Prefer resources we can reach no later than opponent; else nearest overall
    best = None
    best_score = None
    for r in resources:
        if r in obstacles:
            continue
        d_self = cheb((x, y), r)
        d_opp = cheb((ox, oy), r)
        reachable_bonus = 0 if d_self <= d_opp else 1
        score = (reachable_bonus, d_self, abs(r[0] - 3.5) + abs(r[1] - 3.5), r[0], r[1])
        if best_score is None or score < best_score:
            best_score = score
            best = r

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            # Bounds are not guaranteed enforced by us; skip obvious out-of-range moves
            if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
                continue
            if (nx, ny) in obstacles:
                continue
            ds = cheb((nx, ny), (tx, ty))
            moves.append((ds, dx, dy))

    # If all moves blocked, stay
    if not moves:
        return [0, 0]

    # Deterministically choose move that minimizes distance; tie-break by dx then dy
    moves.sort()
    return [int(moves[0][1]), int(moves[0][2])]