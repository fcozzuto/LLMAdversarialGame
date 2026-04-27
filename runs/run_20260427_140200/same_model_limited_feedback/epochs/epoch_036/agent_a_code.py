def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy) ** 0.5

    self_cands = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        self_cands.append((nx, ny, dx, dy))

    if not self_cands:
        return [0, 0]

    # Pick target resources where we are closer than opponent; otherwise prefer resources that deny opponent.
    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = (od - sd)  # positive if we are closer
        # Give strong preference to being closer; still value absolute closeness.
        val = adv * 20 - sd
        # If tied/behind, penalize allowing opponent to easily take it.
        if adv <= 0:
            val = -sd - od * 0.5
        # Deterministic tie-break by coordinates
        if val > best_val or (val == best_val and (rx, ry) < best_target):
            best_val = val
            best_target = (rx, ry)

    if best_target is None:
        # Fallback: move toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = cx, cy
    else:
        tx, ty = best_target

    # Evaluate move options: reduce distance to target; avoid coming too close to opponent; also avoid "passing" behind opponent.
    best_move = (0, 0, 0, 0)
    best_score = -10**18
    for nx, ny, dx, dy in self_cands:
        nd = dist(nx, ny, tx, ty)
        # Prefer resource acquisition: if we step onto a resource, huge boost.
        on_resource = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0
        # Opponent pressure: discourage moving adjacent/into opponent line.
        oppd = dist(nx, ny, ox, oy)
        opp_pen = 0.0
        if oppd <= 1.01:
            opp_pen = 30.0
        # Small tie-breaker to keep deterministic
        tie = (nx + 31 * ny) * 1e-6
        score = (on_resource * 1000.0) - nd * 3.0 + (opp_pen * -1.0) - (1.0 / (1.0 + oppd)) * 2.0 - tie
        if score > best_score:
            best_score = score
            best_move = (nx, ny, dx, dy)

    return [int(best_move[2]), int(best_move[3])]