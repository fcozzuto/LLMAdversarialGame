def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # chebyshev

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_after = dist(nx, ny, ox, oy)

        # Heuristic: if evader, maximize distance and edge pressure; if pursuer, minimize.
        if evader:
            edge = nx + (w - 1 - nx) + ny + (h - 1 - ny)  # smaller near edges
            # Prefer staying near edges when far, away from edges when close.
            edge_bias = (d_after <= 2) * (edge) + (d_after > 2) * (-edge)
            score = d_after * 10 + edge_bias - (dx == 0 and dy == 0) * 2
        else:
            score = -d_after * 10 - (dx == 0 and dy == 0) * 2

        # Deterministic tie-break: lexicographic move preference order already fixed in moves list.
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]