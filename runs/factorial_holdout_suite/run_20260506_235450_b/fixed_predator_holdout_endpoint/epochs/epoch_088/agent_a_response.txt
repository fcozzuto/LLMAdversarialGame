def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v, d=0):
        try:
            return int(v)
        except:
            return d

    sx, sy, ox, oy = ti(sx), ti(sy), ti(ox), ti(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    best_t = None
    best_key = None

    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = ti(r[0]), ti(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        self_d = abs(tx - sx) + abs(ty - sy)
        opp_d = abs(tx - ox) + abs(ty - oy)
        # Prefer cells where we have a clear distance advantage; tie-break by closer to us.
        key = (opp_d - self_d, -self_d)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose the move that best increases our advantage toward the target, while avoiding obstacles.
    cur_self = abs(tx - sx) + abs(ty - sy)
    cur_opp = abs(tx - ox) + abs(ty - oy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ns_self = abs(tx - nx) + abs(ty - ny)
        # If we move closer than opponent can, that’s good; also avoid stepping adjacent to opponent.
        ns_opp = abs(tx - ox) + abs(ty - oy)
        adv = (cur_opp - ns_self) - (cur_opp - cur_self)
        opp_near_pen = 1 if max(abs(nx - ox), abs(ny - oy)) <= 1 else 0
        score = (adv, -ns_self, -opp_near_pen, -(abs(tx - nx) + abs(ty - ny) == ns_self))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]