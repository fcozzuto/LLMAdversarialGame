def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Strategy alternates: even turns secure resources away from opponent; odd turns contest resources near opponent.
    even_turn = (observation.get("turn_index", 0) % 2 == 0)

    best = None
    best_val = None
    for r in resources:
        rx, ry = r[0], r[1]
        ds = max(0, dist((sx, sy), (rx, ry)))
        do = max(0, dist((ox, oy), (rx, ry)))
        # Penalize resources we cannot reach in plausible greedy sense when contested; reward otherwise.
        base = ds - 0.25 * do if even_turn else ds + 0.35 * do
        # Slightly prefer nearer resources regardless
        val = base + 0.05 * (ds * ds)
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    dx = clamp(tx - sx, -1, 1)
    dy = clamp(ty - sy, -1, 1)

    # Try all neighbor moves (including stay), pick best deterministic by evaluation.
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            ns = dist((nx, ny), (tx, ty))
            no = dist((nx, ny), (ox, oy))
            # Favor reducing distance to target; also keep some distance from opponent on even turns, close on odd.
            score = ns
            if even_turn:
                score -= 0.08 * no
            else:
                score += 0.02 * no
                # If we step adjacent to opponent while contesting, prioritize slightly.
                if no <= 1:
                    score -= 0.5
            # Deterministic tie-break: prefer move that matches initial greedy direction.
            score -= 0.01 * (mx == dx) - 0.01 * (my == dy)
            candidates.append((score, mx, my))
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    _, best_mx, best_my = candidates[0] if candidates else (0, 0, 0)
    return [int(best_mx), int(best_my)]