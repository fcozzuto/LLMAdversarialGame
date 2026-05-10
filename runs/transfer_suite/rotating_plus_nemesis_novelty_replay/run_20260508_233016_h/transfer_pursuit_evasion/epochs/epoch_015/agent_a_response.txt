def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = observation.get("self_role", "pursuer") or "pursuer"
    is_evader = str(role).lower().startswith("evad")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    # Prefer "intercept-ish" target: aim slightly beyond opponent in the dominant direction.
    dxo, dyo = ox - sx, oy - sy
    step_x = 1 if dxo > 0 else (-1 if dxo < 0 else 0)
    step_y = 1 if dyo > 0 else (-1 if dyo < 0 else 0)
    tx, ty = ox + step_x, oy + step_y
    if not (0 <= tx < w and 0 <= ty < h):
        tx, ty = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        # Distance metric: Chebyshev (diagonal-friendly)
        d_op = max(abs(nx - ox), abs(ny - oy))
        d_tg = max(abs(nx - tx), abs(ny - ty))

        # Score objective differs by role; keep deterministic tie-breakers.
        if is_evader:
            # maximize survival: increase distance and drift away from target
            key = (-d_op, -d_tg, nx, ny)
        else:
            # pursuer: decrease distance, but also try to be near the "beyond opponent" target
            key = (d_op, d_tg, nx, ny)

        if best_key is None or key < best_key if not is_evader else key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        # fallback: only staying or direct toward opponent if legal
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]
    return best