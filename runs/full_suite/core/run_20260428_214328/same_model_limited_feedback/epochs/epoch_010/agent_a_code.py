def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in moves if dx in (-1, 0, 1) and dy in (-1, 0, 1)]
    res_count = observation.get("remaining_resource_count", len(resources))

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            valid.append((dx, dy))

    # If no resources, head toward center
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_val = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            v = dist(nx, ny, tx, ty)
            if best is None or v < best_val or (v == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), v
        return list(best) if best is not None else [0, 0]

    # Target selection: prefer closest to us; if opponent is closer, consider resources that we can reach soon.
    # Deterministic ordering by ties on coords.
    candidates = []
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # If few resources remain, penalize resources opponent is much closer to.
        # Otherwise, still pick the best reachable option.
        penalty = (do - ds)
        score = (ds, do, penalty)
        candidates.append((score, rx, ry))

    candidates.sort(key=lambda t: (t[0][0], t[0][1], t[1], t[2], t[0][2]))
    target = None
    for score, rx, ry in candidates:
        if res_count <= 4:
            if score[1] <= score[0]:  # opponent not farther than us
                continue
        target = (rx, ry)
        break
    if target is None:
        _, rx, ry = candidates[0]
        target = (rx, ry)
    tx, ty = target

    # Greedy step toward target with obstacle avoidance. If opponent is close to target, slightly bias away.
    ox_to_target = dist(ox, oy, tx, ty)
    best_move = (0, 0)
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_self = dist(nx, ny, tx, ty)
        # Mild repulsion if we let opponent capture; deterministic via comparisons.
        d_opp_after = dist(ox, oy, tx, ty)
        # Encourage getting to target; discourage stalling unless forced.
        stall_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (d_self, stall_pen, (d_opp_after - ox_to_target), abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]