def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    if any(x == sx and y == sy for x, y in res):
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        td = man(ox, oy, tx, ty)
        # maximize advantage (we arrive earlier). Tie-break: closer to target, then closer to block opponent.
        key = (td - sd, -sd, -td, -(tx + ty))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cur_dist = man(sx, sy, tx, ty)
    best_next = (0, 0)
    best_next_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = man(nx, ny, tx, ty)
        # Prefer reducing our distance; also avoid giving the opponent a better race.
        opp_d = man(ox, oy, tx, ty)
        score = (-(nd), (opp_d - nd), -nd, -((nx - tx) ** 2 + (ny - ty) ** 2))
        if best_next_score is None or score > best_next_score or (score == best_next_score and (dx, dy) < best_next):
            best_next_score = score
            best_next = (dx, dy)

    if best_next == (0, 0) and cur_dist > 0:
        # try strict greedy axis step if our heuristic got stuck
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]

    return [best_next[0], best_next[1]]