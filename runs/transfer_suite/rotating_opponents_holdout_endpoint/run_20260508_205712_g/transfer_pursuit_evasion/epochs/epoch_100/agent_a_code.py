def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in sr) or ("runner" in sr)
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Evader: move toward farthest corner from opponent, else maximize distance.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    tx, ty = corner

    best_step = [0, 0]
    best_val = None

    # Tie-break: avoid staying still if tied; then lexicographically smallest (dx,dy).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_op = dist2(nx, ny, ox, oy)
        if is_evader:
            # Prefer farthest from opponent; also prefer moving toward target corner (increase distance from opponent more than raw proximity).
            d_corner_now = dist2(nx, ny, tx, ty)
            d_corner_cur = dist2(sx, sy, tx, ty)
            # Use a shaped objective: keep increasing opponent distance; if equal, move closer to corner.
            val = (d_op * 1000) + (-(d_corner_now) * 1) + (1 if d_corner_now < d_corner_cur else 0)
            better = (best_val is None) or (val > best_val)
        else:
            # Pursuer: minimize opponent distance; if equal, prefer moving toward opponent and away from own corner (less dithering).
            d_op_cur = dist2(sx, sy, ox, oy)
            toward = -dist2(nx, ny, ox, oy) * 1 + (1 if d_op < d_op_cur else 0)
            val = (-d_op * 1000) + toward
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_step = [dx, dy]
        elif best_val is not None:
            # Tie-break
            if val == best_val:
                if best_step == [0, 0] and [dx, dy] != [0, 0]:
                    best_step = [dx, dy]
                elif [dx, dy] != best_step and [dx, dy] < best_step:
                    best_step = [dx, dy]

    return best_step