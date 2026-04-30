def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource that favors us being closer than opponent; otherwise push toward best alternative.
    if resources:
        best_t = resources[0]
        best_v = None
        for r in resources:
            vs = dist((sx, sy), r)
            vo = dist((ox, oy), r)
            # Prefer resources we can reach sooner; if tied, prefer keeping distance from opponent; then nearer.
            v = (vs - vo * 1.15, vs, -dist((ox, oy), (sx, sy)), r[0], r[1])
            if best_v is None or v < best_v:
                best_v = v
                best_t = r
        tx, ty = best_t
    else:
        # No resources: move away from opponent (deterministic).
        tx, ty = (0, 0)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order to break ties.
    moves = sorted(moves, key=lambda m: (m[0], m[1]))
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        # If opponent is closer to target, our best move is still to reduce our distance while keeping space.
        # Also slightly discourage staying still unless clearly optimal.
        stay_pen = 0.2 if (dx == 0 and dy == 0) else 0.0
        # Greedy evaluation; turn_index provides deterministic tie-break.
        v = (d_self + stay_pen, -d_opp, abs(dx) + abs(dy), (observation.get("turn_index", 0) % 7) * 0.0001, dx, dy)
        cand.append((v, [dx, dy]))
    if not cand:
        # All moves blocked: must stay.
        return [0, 0]
    cand.sort(key=lambda t: t[0])
    return cand[0][1]