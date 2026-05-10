def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursu" in self_role) or ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Lead target: one step beyond opponent along vector from self->opponent.
    lx = ox + (1 if ox > sx else (-1 if ox < sx else 0))
    ly = oy + (1 if oy > sy else (-1 if oy < sy else 0))
    if not valid(lx, ly):
        lx, ly = ox, oy

    # If we are pursuer: minimize distance to lead target; also break ties by progress to opponent.
    # If evader: maximize distance from lead target; also break ties by distance from opponent.
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dlead = dist2(nx, ny, lx, ly)
        dop = dist2(nx, ny, ox, oy)
        key = (-dlead, -dop) if pursuer else (dlead, dop)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]
    return best if best is not None else [0, 0]