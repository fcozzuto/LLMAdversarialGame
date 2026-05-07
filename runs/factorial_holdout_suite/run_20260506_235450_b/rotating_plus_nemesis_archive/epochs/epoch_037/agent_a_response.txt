def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < observation.get("grid_width", 8) and 0 <= ny < observation.get("grid_height", 8) and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Prefer moves that maximize immediate "can-be-first" advantage to some resource.
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        candidate_best = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # If opponent is closer, heavily penalize; if we are closer, reward.
            diff = opd - myd
            val = diff * 100 - myd * 2
            if diff < 0:
                val -= (abs(diff) * abs(diff)) * 20
            candidate_best = val if val > candidate_best else candidate_best
        # Small deterministic tie-break: move toward center-ish to reduce being stuck.
        center_bias = -(abs((nx - 3.5)) + abs((ny - 3.5))) * 0.01
        total = candidate_best + center_bias
        if best_val is None or total > best_val or (total == best_val and (dx, dy) < best_move):
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]