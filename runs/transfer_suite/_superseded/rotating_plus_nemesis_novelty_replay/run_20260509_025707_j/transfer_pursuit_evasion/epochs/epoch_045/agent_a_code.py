def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evade = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp_valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: manhattan(c[0], c[1], ox, oy)) if evade else \
             min(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))

    # Deterministic scoring: chase/evade opponent strongly; also favor staying away from obstacles.
    best = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_valid(nx, ny):
            continue
        d_opp = manhattan(nx, ny, ox, oy)
        d_tar = manhattan(nx, ny, target[0], target[1])
        if obstacles:
            d_ob = min(abs(nx - ax) + abs(ny - ay) for ax, ay in obstacles)
        else:
            d_ob = 8

        # Higher is better; negate for pursuer in final comparison by using sign.
        if evade:
            val = (d_opp * 10) + (d_tar * 2) + (d_ob)
        else:
            val = ((-d_opp) * 10) + (-(d_tar) * 0.5) + (d_ob * 0.25)

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    # Fallback: if all blocked, just move within bounds minimizing distance (deterministic).
    if best == (0, 0):
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [int(best[0]), int(best[1])]