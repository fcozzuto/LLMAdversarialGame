def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obst_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        p = 0
        for ex, ey in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d == 0:
                return 10**9
            if d <= 2:
                p += (3 - d) * 60
        return p

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    target = far_corner if is_evader else (ox, oy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18 if is_evader else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, target[0], target[1])
        pen = obst_pen(nx, ny)

        if is_evader:
            # Prefer maximizing distance from pursuer while still heading to the farthest corner.
            score = (d_opp * 3) - d_tgt - pen
            # Mild bias: don't step into immediate obstacle-near cells.
            if pen >= 10**8:
                score -= 10**9
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
        else:
            # Prefer minimizing distance to pursuer; also avoid being blocked by obstacles.
            score = (d_opp * 3) + d_tgt + pen
            if best is None or score < best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        # All moves blocked; deterministically stay.
        return [0, 0]
    return best