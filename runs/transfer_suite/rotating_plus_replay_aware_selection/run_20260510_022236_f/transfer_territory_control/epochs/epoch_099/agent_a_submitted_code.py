def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    scores = observation.get("scores") or {}
    my_score = None
    op_score = None
    if isinstance(scores, dict):
        if "self" in scores:
            my_score = scores.get("self")
            op_score = scores.get("opponent")
        elif "me" in scores:
            my_score = scores.get("me")
            op_score = scores.get("opponent")
    elif isinstance(scores, (list, tuple)) and len(scores) >= 2:
        my_score, op_score = scores[0], scores[1]
    we_lead = True
    try:
        if my_score is not None and op_score is not None:
            we_lead = float(my_score) >= float(op_score)
    except:
        we_lead = True

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, ox, oy)
        sc = -d
        if (nx, ny) in op_terr:
            sc -= 5 if we_lead else 1
        if (nx, ny) in self_terr:
            sc += 1 if we_lead else 0
        if (nx, ny) not in self_terr and (nx, ny) not in op_terr:
            sc += 2 if not we_lead else 1
        if sc > best_sc or (sc == best_sc and (best is None or (dx, dy) < best)):
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best