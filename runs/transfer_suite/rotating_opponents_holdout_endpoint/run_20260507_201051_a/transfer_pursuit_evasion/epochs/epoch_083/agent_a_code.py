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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role) or ("seeker" in role) or ("pursuer" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        tx, ty = ox, oy
    else:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    # Encourage "cutting" through opponent direction rather than oscillating.
    signx = 0 if ox == sx else (1 if ox > sx else -1)
    signy = 0 if oy == sy else (1 if oy > sy else -1)
    desired_dx, desired_dy = signx, signy

    best = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        toward_tx = abs(nx - tx) + abs(ny - ty)
        align = (1 if dx == desired_dx else 0) + (1 if dy == desired_dy else 0)

        # Small deterministic tiebreakers:
        # pursuer: minimize dist, then toward opponent-directed step, then reduce toward target corner if blocked
        # evader: maximize dist, then increase alignment away from pursuer, then maximize distance to target corner
        if is_pursuer:
            val = dist * 1000 - align * 5 + toward_tx
        else:
            val = -dist * 1000 + align * 5 - toward_tx

        if best_val is None or (val < best_val if is_pursuer else val < best_val):
            best_val = val
            best = (dx, dy)

    # If all moves invalid (shouldn't happen), stay put.
    return [int(best[0]), int(best[1])]