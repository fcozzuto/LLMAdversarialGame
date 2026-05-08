def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set_pos(key):
        pts = observation.get(key, []) or []
        out = set()
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    obstacles = to_set_pos("obstacles")
    unclaimed = to_set_pos("unclaimed_cells")
    self_terr = to_set_pos("self_territory")
    opp_terr = to_set_pos("opponent_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - ox) + abs(p[1] - oy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    bestv = -10**18
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = - (abs(nx - tx) + abs(ny - ty))
        if (nx, ny) in unclaimed:
            v += 900
        if (nx, ny) in self_terr:
            v += 200
        if (nx, ny) in opp_terr:
            v += 1600
        # Prefer moving away from opponent slightly when not attacking
        v += 0.05 * (abs(nx - ox) + abs(ny - oy))
        if v > bestv:
            bestv = v
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]