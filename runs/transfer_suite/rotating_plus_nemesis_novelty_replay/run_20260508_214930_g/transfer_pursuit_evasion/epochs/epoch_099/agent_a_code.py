def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    pursuer = not any(k in role for k in ("evader", "runner", "fugitive"))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def manh(x, y): return abs(x - ox) + abs(y - oy)

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = manh(nx, ny)
        # Additional obstacle pressure: discourage moves that put us adjacent to obstacles (more useful when evading).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and blocked(tx, ty):
                    adj_obs += 1
        # Value: pursuer wants smaller d; evader wants larger d, but avoid hugging obstacles too tightly.
        if pursuer:
            val = (-d * 100) - adj_obs
        else:
            val = (d * 100) - (adj_obs * 2)
        # Tie-break: prefer diagonal-ish progress toward/away from opponent deterministically.
        if best is None or val > best or (val == best and (abs(nx - ox) + abs(ny - oy), -dx*dx - dy*dy) < (abs(best_nx - ox) + abs(best_ny - oy), -best_dx*best_dx - best_dy*best_dy)):
            best = val
            best_move = [dx, dy]
            best_nx, best_ny = nx, ny
            best_dx, best_dy = dx, dy

    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]