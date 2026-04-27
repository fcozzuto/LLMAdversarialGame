def choose_move(observation):
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    best = None
    best_val = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources where we are closer; also slightly prefer nearer overall.
        val = (od - sd) * 10 - sd
        if val > best_val:
            best_val = val
            best = (rx, ry)

    # If no resources, head to center to avoid stalls.
    if best is None:
        best = (gw // 2, gh // 2)

    tx, ty = best
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    moves = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
                continue
            if (nx, ny) in obstacles:
                continue
            sd = dist(nx, ny, tx, ty)
            od = dist(nx, ny, ox, oy)
            # Move that keeps/creates lead on target, and slightly increases separation from opponent.
            score = (best_val + (od - sd) * 10 - sd) + od * 0.05 - sd * 0.01
            # Deterministic tie-break: prefer smaller dx then smaller dy then staying (0,0 last).
            moves.append((score, abs(dx), abs(dy), 1 if (dx == 0 and dy == 0) else 0, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(reverse=True)
    return [int(moves[0][4]), int(moves[0][5])]