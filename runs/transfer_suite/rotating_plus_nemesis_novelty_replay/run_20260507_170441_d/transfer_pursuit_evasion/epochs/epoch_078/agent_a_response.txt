def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    d0 = md(sx, sy, ox, oy)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: md(ox, oy, c[0], c[1]))
    else:
        tx, ty = ox, oy

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d1 = md(nx, ny, ox, oy)
        move_towards_x = (nx - sx) * (ox - sx) <= 0 or (ox == sx)
        move_towards_y = (ny - sy) * (oy - sy) <= 0 or (oy == sy)
        diagonal = 1 if dx != 0 and dy != 0 else 0
        border = 1 if (nx in (0, w - 1) or ny in (0, h - 1)) else 0

        if is_evader:
            far_dist = d1
            corner_dist = md(nx, ny, tx, ty)
            score = (far_dist * 10 + corner_dist) + (diagonal * 0.5) - (border * 0.2)
            better = best_score is None or score > best_score
        else:
            towards_x = 0 if move_towards_x else 1
            towards_y = 0 if move_towards_y else 1
            closer = d0 - d1
            score = (-d1 * 10) + (closer * 3) + (towards_x + towards_y) + (diagonal * 0.7) - (border * 0.1)
            better = best_score is None or score > best_score

        if better:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]