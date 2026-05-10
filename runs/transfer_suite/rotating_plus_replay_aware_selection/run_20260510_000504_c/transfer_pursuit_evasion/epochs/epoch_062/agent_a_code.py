def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("purs" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))  # farthest corner from opponent

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = manh(nx, ny, ox, oy)

        if self_is_evader:
            d_tgt = manh(nx, ny, tx, ty)
            key = (d_opp, -d_tgt)  # maximize distance from pursuer; then minimize to escape corner
            better = best_key is None or key > best_key
        else:
            d_tgt = manh(nx, ny, tx, ty)
            key = (-d_opp, -d_tgt)  # minimize distance to opponent; also bias away from far corner to cut space
            better = best_key is None or key > best_key

        if better:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]