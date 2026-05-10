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

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def apply_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            return sx, sy, True
        if (nx, ny) in obstacles:
            return sx, sy, True
        return nx, ny, False

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny, blocked = apply_move(dx, dy)
        d_opp = manh(nx, ny, ox, oy)

        if self_is_evader:
            # Primary: maximize distance from opponent.
            # Secondary: pull toward farthest corner from opponent.
            # Tertiary: avoid stalling when not blocked.
            val = (d_opp, -manh(nx, ny, far_corner[0], far_corner[1]), -int(blocked), -manh(nx, ny, sx, sy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # Pursuer: minimize distance; prefer diagonal progress toward opponent.
            diag_align = (1 if (nx != sx and ny != sy) else 0)
            val = (-d_opp, -diag_align, int(blocked), -manh(nx, ny, ox, oy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]