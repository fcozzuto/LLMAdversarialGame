def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch", "catcher", "runner_chaser"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def clearance(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    c += 1
        return c

    def toward(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return (dx, dy)

    best = None
    best_score = None

    # Simple tie-break: prefer move that aligns toward/away from opponent
    pref = toward(sx, sy, ox, oy)
    if pref not in moves:
        pref = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx, dy]

        c = clearance(nx, ny)
        d = dist2(nx, ny, ox, oy)

        if pursuer:
            # Catch faster; avoid crowding into obstacle boundaries.
            score = (-d * 10.0) + (c * 0.8) + (-0.05 * (abs(nx - ox) + abs(ny - oy)))
        else:
            # Survive longer; increase distance; keep maneuverability near open space.
            score = (d * 10.0) + (c * 0.9) + (0.02 * (abs(nx - ox) + abs(ny - oy)))

        # Deterministic tie-break favoring preferred alignment and smaller move magnitude
        mag = abs(dx) + abs(dy)
        tie = (0 if (dx, dy) == pref else 1, mag, dx, dy)

        if best is None or score > best_score or (score == best_score and tie < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]