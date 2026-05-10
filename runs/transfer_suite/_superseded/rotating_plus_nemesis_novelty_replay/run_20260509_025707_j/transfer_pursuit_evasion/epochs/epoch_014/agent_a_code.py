def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def corner_dist(x, y):
        return min(x + y, x + (h - 1 - y), (w - 1 - x) + y, (w - 1 - x) + (h - 1 - y))

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d = manhattan(nx, ny, ox, oy)
        cd = corner_dist(nx, ny)
        moved_toward = (manhattan(sx, sy, ox, oy) - d)
        dx_sign = 0 if ox == nx else (1 if ox > nx else -1)
        dy_sign = 0 if oy == ny else (1 if oy > ny else -1)
        align = 1 if (dx_sign == (1 if dx > 0 else -1 if dx < 0 else 0) or dx == 0) and (dy_sign == (1 if dy > 0 else -1 if dy < 0 else 0) or dy == 0) else 0

        # Score: pursuer minimizes distance and prefers moves that press toward corners; evader maximizes.
        if is_evader:
            val = (d * 1000) + (cd * 2) + (moved_toward * -5) + (align * 3)
        else:
            val = (-d * 1000) + (-cd * 1) + (moved_toward * 20) + (align * 2)

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if is_evader:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
                elif val == best_val:
                    if (manhattan(nx, ny, ox, oy) > manhattan(best_move[0] + sx, best_move[1] + sy, ox, oy)):
                        best_move = (dx, dy)
            else:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
                elif val == best_val:
                    if (manhattan(nx, ny, ox, oy) < manhattan(best_move[0] + sx, best_move[1] + sy, ox, oy)):
                        best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]