def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    if not targets:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = None
    best_selfd = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        # Evaluate move by best immediate contest score over all remaining resources
        chosen = None
        for tx, ty in targets:
            if not legal(tx, ty):
                continue
            self_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            # Prefer resources we are closer to; if contesting, prefer larger opp advantage reduction
            val = (opp_d - self_d) * 3 - self_d
            if chosen is None or val > chosen[0] or (val == chosen[0] and self_d < chosen[1]):
                chosen = (val, self_d)
        if chosen is None:
            continue
        val, self_d = chosen
        # Tie-break: prefer moves that reduce distance to the nearest reachable target
        nearest_self = min(man(nx, ny, tx, ty) for tx, ty in targets if legal(tx, ty))
        key = (val, -nearest_self)
        if best_val is None or key > (best_val, -best_selfd):
            best_val = val
            best_selfd = nearest_self
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]