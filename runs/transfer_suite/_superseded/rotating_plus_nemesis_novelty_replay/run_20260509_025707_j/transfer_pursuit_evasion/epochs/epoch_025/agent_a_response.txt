def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 2 or h < 2 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0:
            dx = -dx
        dy = y - b
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        d = cheb(nx, ny, ox, oy)
        if is_evader:
            # Maximize distance; minor bias to increase manhattan from opponent and reduce time wasted.
            md = abs(nx - ox) + abs(ny - oy)
            return (d, md)
        else:
            # Minimize distance; tie-break with manhattan and preference to get closer along the dominant direction.
            md = abs(nx - ox) + abs(ny - oy)
            return (-d, -md)

    best_val = None
    best_move = (0, 0)
    # Deterministic tie-break: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = score_move(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]