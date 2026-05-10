def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    opp_dist = lambda x, y: abs(x - ox) + abs(y - oy)
    obs_density = lambda x, y: sum(1 for dx, dy in neigh if (x + dx, y + dy) in obstacles)

    # Small deterministic "escape corridor" based on parity target
    target_x = ox + (1 if ox < w - 1 else -1)
    target_y = oy + (1 if oy < h - 1 else -1)
    target_x = max(0, min(w - 1, target_x))
    target_y = max(0, min(h - 1, target_y))
    parity = (observation.get("turn_index", 0) or 0) & 1
    tx = target_x if parity == 0 else (w - 1 - target_x)
    ty = target_y if parity == 0 else (h - 1 - target_y)

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = opp_dist(nx, ny)
        dens = obs_density(nx, ny)
        center_bias = abs(nx - tx) + abs(ny - ty)
        # Avoid "being boxed in": prefer fewer adjacent obstacles; also reward increasing distance if evader
        if is_evader:
            score = (d * 10) - (dens * 3) - center_bias * 0.2
            # Extra incentive to move roughly away from opponent
            score += (dx * (sx - ox) + dy * (sy - oy)) * 0.5
            better = best_score is None or score > best_score
        else:
            score = (-d * 10) - (dens * 2) + center_bias * -0.05
            score += (-dx * (sx - ox) - dy * (sy - oy)) * 0.5  # move toward opponent direction
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]