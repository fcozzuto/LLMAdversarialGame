def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) and ("evad" not in role)
    if not role:
        pursuer = True

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    tx = 1 if ox > sx else (-1 if ox < sx else 0)
    ty = 1 if oy > sy else (-1 if oy < sy else 0)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = None
    best_score = None
    turn = int(observation.get("turn_index", 0))
    prefer_side = (turn % 2 == 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manh(nx, ny)
        mob = mobility(nx, ny)

        # Primary objective: approach (pursuer) / flee (evader)
        # Secondary: maximize mobility for safety/pressure.
        # Tiebreak: steer in the dominant axis toward the opponent; otherwise side-step alternatingly.
        axis_align = (1 if dx == tx else 0) + (1 if dy == ty else 0)
        side_step = (dx != tx and dy == 0) or (dy != ty and dx == 0) or (dx == -tx and dy == 0) or (dy == -ty and dx == 0)
        side_bonus = 1 if (side_step and prefer_side) else 0

        if pursuer:
            score = (d, -mob, -axis_align, -side_bonus)
            better = best_score is None or score < best_score
        else:
            score = (-d, -mob, axis_align, -side_bonus)
            better = best_score is None or score < best_score

        if better:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best