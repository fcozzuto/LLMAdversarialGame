def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    # If role unclear, assume pursuer behavior (best for pursuit_evasion curriculum)
    if ("pursuer" in role) or ("hunter" in role) or ("seeker" in role) or ("catch" in role):
        is_evader = False

    candidates = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_val = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        # Prefer closer (pursuer) / farther (evader); tie-break deterministically by cheb then turn-based bias
        target = man if (w <= 9 and h <= 9) else cheb
        val = target if not is_evader else -target

        # Additional bias: move to reduce/keep relative direction stability
        # (keeps deterministic behavior under ties)
        orient = (nx - sx) * (ox - sx) + (ny - sy) * (oy - sy)
        val += (-1 if is_evader else 1) * 0.001 * orient

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]