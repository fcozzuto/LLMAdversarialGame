def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # tie-break deterministically by fixed move order

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def score(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        # If evader, we want to maximize distance (minimize capture pressure)
        # If pursuer, minimize distance.
        base = d if not pursuer else -d
        # Large penalty if landing on obstacle (though engine will keep in place on invalid moves)
        if (nx, ny) in obstacles:
            base -= 10**6 if pursuer else -10**6
        # Prefer moves that keep away from obstacles when evading; prefer moves toward obstacles when pursuing slightly (deterministic)
        if obstacles:
            min_do = 10**9
            for bx, by in obstacles:
                dd = abs(nx - bx) + abs(ny - by)
                if dd < min_do: min_do = dd
            # For evader: higher min distance to obstacle is safer; for pursuer: lower is a mild bias (can help trap)
            base += (min_do if not pursuer else -min_do) * 0.1
        return base

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        sc = score(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]