def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = observation.get("self_role", "") or ""

    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    if "purs" in role.lower():
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d2 = dist2(nx, ny)
            # Prefer closer; then reduce remaining displacement components
            score = (-d2, -abs(nx - ox) - abs(ny - oy))
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # Evader: maximize distance; avoid moves that reduce freedom too much near obstacles
        def freedom(nx, ny):
            cnt = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty):
                    cnt += 1
            return cnt

        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d2 = dist2(nx, ny)
            # Prefer larger distance; then more freedom; then keep move away in both axes
            score = (d2, freedom(nx, ny), abs(nx - ox) + abs(ny - oy))
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]