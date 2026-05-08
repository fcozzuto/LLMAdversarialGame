def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "") or (("direct" in role) and ("evad" not in role))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def corner_score(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    def valid(nx, ny):
        return inside(nx, ny) and (nx, ny) not in oset

    if self_is_pursuer:
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if nx == ox and ny == oy:
                return [dx, dy]
            d = manh(nx, ny, ox, oy)
            # Predict: avoid moving into a square where opponent can capture us next.
            unsafe = 0
            for pdx, pdy in moves:
                px, py = ox + pdx, oy + pdy
                if valid(px, py) and px == nx and py == ny:
                    unsafe = 1
                    break
            # Tie-break: reduce distance, prefer diagonal alignment, and keep away from corners slightly.
            align = -((dx != 0 and dy != 0) * 1)
            key = (unsafe, d, align, -corner_score(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Evader: maximize distance; also prefer moving toward the farthest corner from pursuer.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        # Avoid immediate capture (pursuer moving into us next).
        unsafe = 0
        for pdx, pdy in moves:
            px, py = ox + pdx, oy + pdy
            if valid(px, py) and px == nx and py == ny:
                unsafe = 1
                break
        # If equal distance, push toward farthest corner; deterministic tie-break.
        key = (unsafe, -d, -corner_score(nx, ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]