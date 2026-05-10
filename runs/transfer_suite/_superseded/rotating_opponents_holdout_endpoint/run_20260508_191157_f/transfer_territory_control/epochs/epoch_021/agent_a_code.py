def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = list(opp_terr) if opp_terr else [(ox, oy)]
    if not targets:
        targets = [(ox, oy)]
    best_t = targets[0]
    best_d = 10**9
    for tx, ty in targets[:32]:
        d = manh(sx, sy, tx, ty)
        if d < best_d:
            best_d = d
            best_t = (tx, ty)
    tx, ty = best_t

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = manh(nx, ny, tx, ty)
        val = -d
        if (nx, ny) in unclaimed:
            val += 2
        if (nx, ny) in self_terr:
            val += 1
        if (nx, ny) == (sx, sy):
            val -= 0.1
        if val > best_val + 1e-12:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]