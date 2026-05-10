def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    if (sx, sy) == (ox, oy):
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0, 3))
            else:
                # deterministic tie-break: axis-aligned preferred
                diag = 1 if (dx != 0 and dy != 0) else 0
                moves.append((dx, dy, diag))

    best_move = (0, 0, 10**9)
    best_val = -10**18 if is_evader else 10**18

    for dx, dy, diag in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ndx, ndy = ox - nx, oy - ny
        dist = max(abs(ndx), abs(ndy))  # capture at radius 0; Chebyshev works well on grid
        # Secondary tie: prefer moves that change x and y consistently towards/away from opponent
        dot = ndx * (1 if dx > 0 else (-1 if dx < 0 else 0)) + ndy * (1 if dy > 0 else (-1 if dy < 0 else 0))
        # For pursuer minimize dist; for evader maximize dist
        val = dist if is_evader else -dist
        val += (0.001 * dot) + (0.0001 * (-diag))  # tiny deterministic preferences
        if (is_evader and val > best_val) or ((not is_evader) and val > best_val):
            best_val = val
            best_move = (dx, dy, diag)

    dx, dy, _ = best_move
    return [int(dx), int(dy)]