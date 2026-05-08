def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p
            obs_set.add((int(x), int(y)))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_to_opp = manhattan(nx, ny, ox, oy)
        d_to_self = manhattan(nx, ny, sx, sy)
        corner_bonus = 0
        if (nx == 0 or nx == w - 1) and (ny == 0 or ny == h - 1):
            corner_bonus = 50
        val = d_to_opp * 10 + corner_bonus - d_to_self
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]