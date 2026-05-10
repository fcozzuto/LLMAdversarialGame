def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("run" in role) or ("hide" in role) or ("runner" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        corner_bonus = max(nx, w - 1 - nx) + max(ny, h - 1 - ny)  # prefer corners deterministically
        val = dist + (0.01 * corner_bonus)
        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if is_evader:
                # maximize distance; tie-break lexicographically by (dx,dy) for determinism
                if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                    best_val = val
                    best_move = [dx, dy]
            else:
                # minimize distance to capture; tie-break lexicographically by (dx,dy)
                if val < best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                    best_val = val
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]