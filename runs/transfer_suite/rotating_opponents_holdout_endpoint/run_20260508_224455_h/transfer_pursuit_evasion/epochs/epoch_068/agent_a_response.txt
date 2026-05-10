def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, dict):
            x, y = int(p.get("x", -1)), int(p.get("y", -1))
        else:
            x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    role = str(observation.get("self_role") or observation.get("role") or "")
    is_evader = ("evader" in role.lower()) or ("escape" in role.lower())

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_now = abs(nx - ox) + abs(ny - oy)
        # In addition to distance, bias toward "side" squares when pursuer to reduce opponent options.
        if is_evader:
            val = d_now
            # discourage moving toward the opponent if tied
            val += -0.01 * (nx + ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # pursuer: chase, but also avoid stepping into dead-ends next to obstacles
            nbrs_blocked = 0
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                tx, ty = nx + adx, ny + ady
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
                    nbrs_blocked += 1
            val = d_now + 0.02 * nbrs_blocked
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]