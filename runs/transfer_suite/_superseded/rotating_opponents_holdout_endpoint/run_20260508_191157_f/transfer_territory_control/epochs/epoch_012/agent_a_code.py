def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = observation.get("resources") or []
    rem = observation.get("remaining_resource_count", None)
    self_path = observation.get("self_path") or []
    opp_path = observation.get("opponent_path") or []

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    def best_target(cells):
        if not cells:
            return None
        bx = by = None
        bd = 10**9
        for x, y in cells:
            if (x, y) in obstacles:
                continue
            d = dist(sx, sy, x, y)
            if d < bd or (d == bd and (x, y) < (bx, by)):
                bd = d
                bx, by = x, y
        return (bx, by) if bx is not None else None

    target = None
    if resources and (rem is None or rem > 0):
        target = best_target([tuple(p) for p in resources])
    if target is None:
        target = best_target(list(unclaimed))

    tx, ty = target if target is not None else (ox, oy)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if target is not None:
            val += -dist(nx, ny, tx, ty) * 3
        val += dist(nx, ny, ox, oy) * 1  # avoid opponent
        if (nx, ny) in unclaimed:
            val += 6
        if rem is not None and resources and (nx, ny) in set(tuple(p) for p in resources):
            val += 50
        if (nx, ny) in set(tuple(p) for p in (self_path[-10:] if self_path else [])):
            val -= 2
        if (nx, ny) in set(tuple(p) for p in (opp_path[-10:] if opp_path else [])):
            val -= 2
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]