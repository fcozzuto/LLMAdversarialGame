def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    evader_mode = ("evader" in self_role) or ("runner" in self_role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def open_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def corner_target():
        if evader_mode:
            # Prefer being far from pursuer by targeting the farthest corner from opponent.
            return max(corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))
        # If pursuer, target the corner closest to opponent (helps cutting off).
        return min(corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))

    tx, ty = corner_target()

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
        d = max(abs(nx - ox), abs(ny - oy))  # Chebyshev capture metric (radius 0)
        prog = abs(nx - tx) + abs(ny - ty)  # steer to target corner depending on role
        openv = open_count(nx, ny)

        if evader_mode:
            # Maximize distance; also drift toward corner that is far from opponent; keep mobility.
            score = (d * 1000) + (-prog) + (openv * 2)
        else:
            # Minimize distance; also reduce distance to opponent's corner; keep mobility.
            score = (-d * 1000) + (-prog) + (openv * 2)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]