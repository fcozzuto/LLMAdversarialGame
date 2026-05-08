def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    if not self_is_evader:
        orr = str(observation.get("opponent_role", "")).lower()
        if ("evader" in orr) or ("runner" in orr):
            self_is_evader = False

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    # Deterministic target corner: farthest (tie by lexicographic)
    tx, ty = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), -c[0], -c[1]))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_sc = -10**18 if self_is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dpo = abs(nx - ox) + abs(ny - oy)
        dtc = abs(nx - tx) + abs(ny - ty)
        # Small tie-breakers: prefer staying closer to corner when evading, and lower movement when pursuing
        step_pen = abs(dx) + abs(dy) * 0.1
        if self_is_evader:
            sc = 2.2 * dpo + 0.9 * dtc - step_pen
            if sc > best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
        else:
            sc = 2.2 * dpo + 0.3 * dtc + step_pen
            if sc < best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]