def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("direct" in role and "evad" not in role)
    # Fallback: if not sure, behave like pursuer (works with given improvement trend).
    if not role:
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    cur = d2(sx, sy)
    best = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue
        nd = d2(nx, ny)

        if is_pursuer:
            # Prefer decreasing distance; if tied, avoid staying and avoid increasing.
            key = (nd, 0 if nd <= cur else 1, 1 if (dx == 0 and dy == 0) else 0)
        else:
            # Evader: prefer increasing distance; if tied, avoid staying and avoid decreasing.
            key = (-nd, 0 if nd >= cur else 1, 1 if (dx == 0 and dy == 0) else 0)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]